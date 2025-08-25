from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog
from PyQt5.QtCore import Qt
import os


class MyTreeWidget(QTreeWidget):
    def __init__(self, parent=None, display_exp=None, display_range=None, items=None, remove_folders_callback=None, move_exp_callback=None):
        super().__init__(parent)
        self.setHeaderHidden(True)  # Masque le titre
        self.display_exp = display_exp
        self.display_range = display_range
        self.remove_folders_callback = remove_folders_callback
        self.move_exp_callback = move_exp_callback

        self.itemClicked.connect(self.on_click_item)

        self.all_items = []

        if items is not None:
            self.populate(items)

        # contextual menu on right click
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def on_click_item(self, item, column):
        # Vérifie si l'item a des enfants
        if item.childCount() == 0:
            # vérifier si il y a un parent
            full_path = self.get_full_path(item)
            self.display_exp(full_path)
            self.display_range()

    def expand_parents(self, item):
        parent = item.parent()
        while parent:
            parent.setExpanded(True)
            parent = parent.parent()

    def get_full_path(self, item):
        parts = []
        while item:
            parts.insert(0, item.text(0))
            item = item.parent()

        return os.path.join(*parts) if parts else ""
        return "/".join(parts)

    def populate(self, items):
        self.clear()
        # for entry in items:
        for entry in sorted(items, key=lambda e: list(e.keys())[0].lower() if isinstance(e, dict) else str(e).lower()):
            self._add_entry(entry, self)

    def _add_entry(self, entry, parent_widget):
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
        """
        Affiche uniquement les éléments (et leurs parents) qui correspondent au texte.
        Seuls les enfants correspondants sont inclus.
        """
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

        self.populate(filtered)

    def get_expanded_items(self):
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
        # Ex: return a tuple with column texts
        return tuple(item.text(i) for i in range(item.columnCount()))

    def restore_expanded_items(self, expanded_ids):
        def recurse(item):
            if self.get_item_identifier(item) in expanded_ids:
                item.setExpanded(True)
            for i in range(item.childCount()):
                recurse(item.child(i))

        for i in range(self.topLevelItemCount()):
            recurse(self.topLevelItem(i))

    def get_group_names(self):
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
        item = self.itemAt(pos)
        if item is None:
            return

        item_data = self.get_clicked_item_data(item)

        full_path = self.get_full_path(item)

        menu = QMenu(self)

        # Ajouter des actions au menu contextuel
        action_rm = menu.addAction("Remove")

        move_menu = menu.addMenu("Move to")
        groups = self.get_group_names()
        if groups:
            for group in groups:
                move_menu.addAction(group, lambda g=group: self.move_exp_callback(full_path, g))
        move_menu.addAction("Create new group", lambda: self.move_to_new_group_dialog(full_path))

        action = menu.exec_(self.mapToGlobal(pos))

        if action == action_rm:
            # item.setExpanded(True)
            # self.remove_exp_callback(full_path)
            self.remove_folders_callback(item_data)

    def move_to_new_group_dialog(self, full_path):
        # Open a dialog to create a new group
        group_name, ok = QInputDialog.getText(self, 'New Group', 'Enter group name:')
        if ok and group_name:
            return self.move_exp_callback(full_path, group_name)
        return None

    def get_clicked_item_data(self, item):
        """
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
