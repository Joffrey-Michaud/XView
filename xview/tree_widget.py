"""Tree widget to browse experiment groups and items with context actions."""

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt
import os
from xview.compare_window import ComparisonWindow


class MyTreeWidget(QTreeWidget):
    """QTreeWidget with helpers to populate, filter, and context-menu actions."""

    def __init__(self, parent=None, display_exp=None, display_range=None, items=None, remove_folders_callback=None, move_exp_callback=None, copy_exp_callback=None):
        super().__init__(parent)
        self.setHeaderHidden(True)  # Masque le titre
        # Rendre explicite le mode de sélection pour éviter les surprises
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.display_exp = display_exp
        self.display_range = display_range
        self.remove_folders_callback = remove_folders_callback
        self.move_exp_callback = move_exp_callback
        self.copy_exp_callback = copy_exp_callback

        self.itemClicked.connect(self.on_click_item)

        self.all_items = []

        if items is not None:
            self.populate(items)

        # contextual menu on right click
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.comparison_window = None

    def on_click_item(self, item, column):
        """Select-only items (leaf nodes) trigger the display callbacks."""
        # Vérifie si l'item a des enfants
        if item.childCount() == 0:
            # vérifier si il y a un parent
            full_path = self.get_full_path(item)
            self.display_exp(full_path)
            self.display_range()

    def expand_parents(self, item):
        """Expand all parents up to the root for a given item."""
        parent = item.parent()
        while parent:
            parent.setExpanded(True)
            parent = parent.parent()

    def get_full_path(self, item):
        """Build the relative path represented by a tree node."""
        parts = []
        while item:
            parts.insert(0, item.text(0))
            item = item.parent()

        return os.path.join(*parts) if parts else ""
        return "/".join(parts)

    def populate(self, items):
        """Fill the tree from a nested list/dict structure (groups and names)."""
        self.clear()
        for entry in sorted(items, key=lambda e: list(e.keys())[0].lower() if isinstance(e, dict) else str(e).lower()):
            self._add_entry(entry, self)

    def _add_entry(self, entry, parent_widget):
        """Recursive helper to add items and groups to the tree."""
        if isinstance(entry, str):
            item = QTreeWidgetItem([entry])
            if parent_widget == self:
                self.addTopLevelItem(item)
            else:
                parent_widget.addChild(item)
        elif isinstance(entry, dict):
            for key, children in entry.items():
                item = QTreeWidgetItem([key])
                matched_children = []
                # for child in children:
                for child in sorted(children, key=lambda c: list(c.keys())[0].lower() if isinstance(c, dict) else str(c).lower()):
                    added = self._add_entry(child, item)
                    if added:
                        matched_children.append(added)

                if matched_children:
                    if parent_widget == self:
                        self.addTopLevelItem(item)
                    else:
                        parent_widget.addChild(item)
                    return item  # important pour filtrage récursif
                elif parent_widget == self and not children:
                    self.addTopLevelItem(item)
                    return item
        return item if isinstance(entry, str) else None

    def filter_items(self, text):
        """Filter items to show only matches (and their parents) for the text."""
        text = text.lower()

        def filter_entry(entry):
            if isinstance(entry, str):
                return entry.lower().find(text) >= 0
            elif isinstance(entry, dict):
                result = {}
                for key, children in entry.items():
                    # Filter children recursively and keep transformed filtered nodes
                    filtered_children = []
                    for child in children:
                        child_filtered = filter_entry(child)
                        if child_filtered:
                            # If child is a dict, child_filtered is a dict to keep nested filters
                            if isinstance(child, dict):
                                filtered_children.append(child_filtered)
                            else:
                                # child is a string that matched
                                filtered_children.append(child)

                    # If the group name matches, keep it and ensure it's expandable
                    if text in key.lower():
                        # Prefer filtered children when available; otherwise include all to allow expansion
                        result[key] = filtered_children if filtered_children else children
                    elif filtered_children:
                        result[key] = filtered_children
                return result if result else False
            return False

        # Appliquer le filtre
        filtered = []
        for entry in self.all_items:
            filtered_entry = filter_entry(entry)
            if filtered_entry:
                if isinstance(filtered_entry, dict):
                    filtered.append(filtered_entry)
                else:
                    filtered.append(entry)

    def get_expanded_items(self):
        """Return identifiers of currently expanded items (for later restore)."""
        expanded_items = []

        def recurse(item):
            if item.isExpanded():
                expanded_items.append(self.get_item_identifier(item))
            for i in range(item.childCount()):
                recurse(item.child(i))

        for i in range(self.topLevelItemCount()):
            recurse(self.topLevelItem(i))
        return expanded_items

    def get_item_identifier(self, item):
        """Build a stable identifier tuple using the item texts."""
        # Ex: return a tuple with column texts
        return tuple(item.text(i) for i in range(item.columnCount()))

    def restore_expanded_items(self, expanded_ids):
        """Expand back the items whose identifiers appear in expanded_ids."""
        def recurse(item):
            if self.get_item_identifier(item) in expanded_ids:
                item.setExpanded(True)
            for i in range(item.childCount()):
                recurse(item.child(i))

        for i in range(self.topLevelItemCount()):
            recurse(self.topLevelItem(i))

    def get_parent_group_name(self, item):
        """Return the immediate parent group name, or None for top-level groups."""
        parent = item.parent()
        if parent is not None:
            return parent.text(0)
        return None

    def get_group_names(self):
        """Return all group names by traversing the tree recursively."""
        groups = []

        def recurse(item):
            if item.childCount() > 0:
                groups.append(item.text(0))
                for i in range(item.childCount()):
                    recurse(item.child(i))

        for i in range(self.topLevelItemCount()):
            recurse(self.topLevelItem(i))

        return sorted(groups)

    def show_context_menu(self, pos):
        """Display a context menu to move/copy/compare or remove items."""
        item = self.itemAt(pos)
        if item is None:
            return

        item_data = self.get_clicked_item_data(item)
        full_path = self.get_full_path(item)

        # Precompute info to avoid accessing a potentially deleted QTreeWidgetItem later
        item_name = item.text(0)
        is_group = (item.childCount() > 0) or (len(item_data) > 1)
        children_to_remove = max(0, len(item_data) - 1)
        current_group = self.get_parent_group_name(item)

        menu = QMenu(self)

        # Ajouter des actions au menu contextuel

        move_menu = menu.addMenu("Move to")
        groups = self.get_group_names()
        if groups:
            for group in groups:
                move_menu.addAction(group, lambda g=group: self.move_exp_callback(full_path, g))
        move_menu.addAction("Create new group", lambda: self.move_to_new_group_dialog(full_path))

        copy_menu = menu.addMenu("Copy to")
        # Pour la copie, exclure le groupe actuel de l'expérience
        available_groups_for_copy = [g for g in groups if g != current_group] if groups else []
        if available_groups_for_copy:
            for group in available_groups_for_copy:
                copy_menu.addAction(group, lambda g=group: self.copy_exp_callback(full_path, g))
        copy_menu.addAction("Create new group", lambda: self.copy_to_new_group_dialog(full_path))

        compare_action = None
        if item.childCount() > 0:
            compare_action = menu.addAction("Compare")

        action_rm = menu.addAction("Remove")

        action = menu.exec_(self.mapToGlobal(pos))

        if action == action_rm:
            if self.confirm_removal(item_name, is_group, children_to_remove):
                self.remove_folders_callback(item_data)
        elif compare_action is not None and action == compare_action:
            self.compare_exp_from_group(full_path)

    def confirm_removal(self, item_name, is_group, children_to_remove=0):
        """Ask for confirmation before removing an experiment or a group."""
        if is_group:
            text = f"Supprimer le groupe « {item_name} » et {children_to_remove} élément(s) ?"
        else:
            text = f"Supprimer « {item_name} » ?"

        reply = QMessageBox.question(
            self,
            "Confirmation",
            text,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes

    def compare_exp_from_group(self, group_path):
        """Open a comparison window for all experiments inside the group."""
        comp_window = ComparisonWindow(group_path=group_path)
        comp_window.exec_()

    def move_to_new_group_dialog(self, full_path):
        """Prompt for a new group name and move the selected item to it."""
        # Open a dialog to create a new group
        group_name, ok = QInputDialog.getText(self, 'New Group', 'Enter group name:')
        if ok and group_name:
            return self.move_exp_callback(full_path, group_name)
        return None

    def copy_to_new_group_dialog(self, full_path):
        """Prompt for a new group name and copy the selected item to it."""
        # Open a dialog to create a new group for copying
        group_name, ok = QInputDialog.getText(self, 'New Group', 'Enter group name:')
        if ok and group_name:
            return self.copy_exp_callback(full_path, group_name)
        return None

    def get_clicked_item_data(self, item):
        """Return selected data paths for use by callbacks.

        Returns:
        - A list of subfolders if the item is a group (has children).
        - A list containing a single element (the full path) if the item is an experience (has no children).
        """
        if item.childCount() > 0:  # It's a group
            base_group_folder = self.get_full_path(item)
            subfolders = []
            for i in range(item.childCount()):
                child_item = item.child(i)
                # If you want the full path of the immediate children:
                subfolders.append(self.get_full_path(child_item))
                # Or if you just want the name of the immediate children:
                # subfolders.append(child_item.text(0))
            subfolders.append(base_group_folder)
            return subfolders
        else:  # It's an experience
            return [self.get_full_path(item)]

    # def remove_data(self, folders_to_rm):
    #     print("Folders to remove:", folders_to_rm)
