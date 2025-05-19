from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
import os


class MyTreeWidget(QTreeWidget):
    def __init__(self, parent=None, display_exp=None, items=None):
        super().__init__(parent)
        self.setHeaderHidden(True)  # Masque le titre
        self.display_exp = display_exp

        self.itemClicked.connect(self.on_click_item)

        self.all_items = []

        if items is not None:
            self.populate(items)

        # # Ajouter les éléments principaux
        # self.add_top_level_items()

    def on_click_item(self, item, column):
        # Vérifie si l'item a des enfants
        if item.childCount() == 0:
            # vérifier si il y a un parent
            full_path = self.get_full_path(item)
            self.display_exp(full_path)

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
        for entry in items:
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
                for child in children:
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
                    filtered_children = [
                        c for c in children if filter_entry(c)
                    ]
                    if text in key.lower() or filtered_children:
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


    # def add_top_level_items(self):
    #     item_a = QTreeWidgetItem(["A"])
    #     item_b = QTreeWidgetItem(["B"])
    #     item_c = QTreeWidgetItem(["C"])

    #     # Sous-éléments pour B
    #     item_b1 = QTreeWidgetItem(["B1"])
    #     item_b2 = QTreeWidgetItem(["B2"])
    #     item_b.addChildren([item_b1, item_b2])

    #     self.addTopLevelItems([item_a, item_b, item_c])

