from functools import partial
from itertools import groupby
from operator import attrgetter

from django.db import models
from django.forms.models import (ModelChoiceField, ModelChoiceIterator,
                                 ModelMultipleChoiceField)

from accountancy.descriptors import DecimalDescriptor, UIDecimalDescriptor

"""
MODEL FIELDS
"""

class AccountsDecimalField(models.DecimalField):
    """
    I want decimal fields in forms to show as blank by default.
    But I don't want the DB to save the value as null.

    This field will ensure a decimal of 0 is saved to the DB instead
    of null.
    """

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)
        setattr(cls, self.name, DecimalDescriptor(self.name))


class UIDecimalField(AccountsDecimalField):
    """
    This field includes a method which flips the sign of the value stored in DB
    so it looks right in the UI.
    """

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)
        setattr(cls, f"ui_{self.name}", UIDecimalDescriptor(self.name))


class RootAndLeavesModelChoiceIterator(ModelChoiceIterator):
    """
    Based on the Xero accounts software we wish to show a
    list of account nominals where an account structure like -

        Assets
            Current Assets
                Bank Account

    Would show as

        Assets
            Bank Account

    In order words, get all the roots in the nominal tree
    structure, and get all the leaves for each root.
    """

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        tree = self.queryset  # must be Model.objects.all().prefetch_related('children')
        leaves = []
        root_and_leaves = (None, leaves)
        for node in tree:
            if node.is_root_node():
                if leaves:
                    yield root_and_leaves
                    leaves = []
                root_and_leaves = (node.name, leaves)
            elif node.level == 2:
                leaves.append(self.choice(node))
        yield root_and_leaves

    def __len__(self):
        length = 0
        tree = self.queryset
        for node in tree:
            if node.is_root_node() or node.level == 2:
                length = length + 1
        return length + (1 if self.field.empty_label is not None else 0)


class RootAndChildrenModelChoiceIterator(ModelChoiceIterator):
    """
    When creating nominal codes one needs to tick the account type i.e.
    a direct child of a root.  Again this is based on Xero.

        E.g.

            Assets
                Current Assets
                    Bank


        If the user were to create Bank, they would select "Current Assets" from
        the dropdown.  "Assets" would not show.
    """

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        tree = self.queryset  # must be Model.objects.all().prefetch_related('children')
        children = []
        root_and_children = (None, children)
        for node in tree:
            if node.is_root_node():
                if children:
                    yield root_and_children
                    children = []
                root_and_children = (node.name, children)
            elif node.level == 1:
                children.append(self.choice(node))
        yield root_and_children

    def __len__(self):
        length = 0
        tree = self.queryset
        for node in tree:
            if node.is_root_node() or node.level == 1:
                length = length + 1
        return length + (1 if self.field.empty_label is not None else 0)


class ModelChoiceIteratorWithFields(ModelChoiceIterator):

    """

        ModelChoiceIterator gives us the value - usually the primary key of the object -
        and the label.  But when the user chooses a vat code object we also need to know
        the Vat rate, which is an attribute of the model.

        This iterator will give us -

            (value, label, [ (object_attr, object_attr_value), (object_attr, object_attr_value) ])

        It is envisaged the widget will have a lookup field attribute dictionary for picking
        which of these it needs and then add them as data attributes to the option html.
        If we already have a value we also need to add the data attributes.

        So the widget code -

            for value, label, *model_attrs in self.choices:
                # do stuff
                if *model_attrs:
                    pass

    """

    def choice(self, obj):
        c = super().choice(obj)  # ('< class ModelChoiceIteratorValue>', 'some_label')
        value, label = c
        d = obj.__dict__
        tmp = []
        for field, val in d.items():
            tmp.append((field, val))
        d = d["_state"].__dict__
        if d.get("fields_cache"):
            related = d["fields_cache"]
            for related_name, related_obj in related.items():
                d = related_obj.__dict__
                for field, val in d.items():
                    tmp.append((related_name + "__" + field, val))
        return (value, label, tmp)


class ChooseIteratorMixin:
    def __init__(self, *args, **kwargs):
        iterator = kwargs.pop("iterator")
        super().__init__(*args, **kwargs)
        self.iterator = iterator


class ModelChoiceFieldChooseIterator(ChooseIteratorMixin, ModelChoiceField):
    pass


class ModelMultipleChoiceFieldChooseIterator(ChooseIteratorMixin, ModelMultipleChoiceField):
    pass
