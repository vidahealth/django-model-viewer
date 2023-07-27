from functools import partial
from itertools import filterfalse

from django.db import models

class DjangoModelViewer:
    def __init__(self, data_type: models.Model):
        self._data_type = data_type

    @property
    def data_type(self):
        return self._data_type

    def _filter_attributes(self, fields, exclude=False):

        if exclude:
            method = filterfalse
        else:
            method = filter

        filtered_fields = method(lambda e: getattr(e, "is_relation", False), fields)
        return filtered_fields

    @property
    def attributes(self):
        fields = self.data_type._meta.fields
        filtered_fields = filterfalse(
            lambda e: getattr(e, "is_relation", False), fields
        )

        return filtered_fields

    @property
    def relation_attributes(self):
        fields = self.data_type._meta.fields + self.data_type._meta.many_to_many
        filtered_fields = filter(lambda e: getattr(e, "is_relation", False), fields)

        return filtered_fields

    @property
    def relationships(self):
        return self.data_type._meta.related_objects

    @property
    def attribute_list(self):
        """
        list of non relation attributes
        """
        self.attribute_field_size = {"name": 0, "type": 0, "null": 0}

        result = []
        for attribute in self.attributes:
            data_type_name = type(attribute).__name__
            record = {
                "name": attribute.name,
                "type": data_type_name,
                "null": attribute.null,
            }

            self.attribute_field_size["name"] = max(
                self.attribute_field_size["name"], len(record["name"])
            )
            self.attribute_field_size["type"] = max(
                self.attribute_field_size["type"], len(record["type"])
            )

            result.append(record)

        return result

    @property
    def relation_attribute_list(self):
        """
        list of relation attributes
        """
        result = []
        for relationship in self.relation_attributes:

            data_type_name = "to One"
            through_name = ""

            if type(relationship).__name__ in ["ManyToManyField"]:
                data_type_name = "to Many"
                through_name = relationship.remote_field.through.__name__

            related_name = relationship.remote_field.related_name
            inverse = related_name if related_name else "No Inverse"

            record = {
                "name": relationship.name,
                "destination": relationship.related_model.__name__,
                "inverse": inverse,
                "type": data_type_name,
                "through": through_name,
            }
            result.append(record)

        return result

    @property
    def relationship_list(self):
        """
        * - denotes reverse relation via destination class
        """
        result = []
        for relationship in self.relationships:

            data_type_name = "to One *"
            through_name = ""

            if type(relationship).__name__ in ["ManyToManyRel", "ManyToOneRel"]:
                data_type_name = "to Many *"

            if type(relationship).__name__ == "ManyToManyRel":
                through_name = relationship.through.__name__

            accessor_name = relationship.get_accessor_name()
            if relationship.related_name is None:
                related_name = f"~ {accessor_name}"
            else:
                related_name = accessor_name

            record = {
                "name": related_name,
                "destination": relationship.related_model.__name__,
                "inverse": relationship.field.name,
                "type": data_type_name,
                "through": through_name,
            }

            result.append(record)

        return result

    def print_attributes(self, sort=True, reverse=False):
        attributes_list = self.attribute_list
        if sort:
            attributes_list.sort(key=lambda e: e["name"], reverse=reverse)

        k_name = "name"
        k_type = "type"
        k_null = "null"

        name_max_size = len(k_name)
        type_max_size = len(k_type)
        null_max_size = len(str(False))

        for r in attributes_list:
            name_max_size = max(name_max_size, len(r[k_name]))
            type_max_size = max(type_max_size, len(r[k_type]))

        output_template = (
            "{name:{name_max_size}} {type:{type_max_size}} {null:{null_max_size}}"
        )
        partial_output_template = partial(
            output_template.format,
            name_max_size=name_max_size,
            type_max_size=type_max_size,
            null_max_size=null_max_size,
        )

        print(partial_output_template(name=k_name, type=k_type, null=k_null))
        print("=" * name_max_size, "=" * type_max_size, "=" * 5)

        if attributes_list:
            for r in attributes_list:
                print(
                    partial_output_template(
                        name=r[k_name],
                        type=r[k_type],
                        null=str(r[k_null]) if r[k_null] else "",
                    )
                )
        else:
            print("<None>")

    def print_relationships(self, sort=True, reverse=False):
        relationship_list = self.relationship_list
        relation_attribute_list = self.relation_attribute_list

        combined_relationship_list = relationship_list + relation_attribute_list

        if sort:
            combined_relationship_list.sort(key=lambda e: e["name"], reverse=reverse)

        k_name = "name"
        k_destination = "destination"
        k_inverse = "inverse"
        k_type = "type"
        k_through = "through"

        name_max_size = len(k_name)
        destination_max_size = len(k_destination)
        inverse_max_size = len(k_inverse)
        type_max_size = len(k_type)
        through_max_size = len(k_through)

        for r in combined_relationship_list:
            name_max_size = max(name_max_size, len(r[k_name]))
            destination_max_size = max(destination_max_size, len(r[k_destination]))
            inverse_max_size = max(inverse_max_size, len(r[k_inverse]))
            type_max_size = max(type_max_size, len(r[k_type]))
            through_max_size = max(through_max_size, len(r[k_through]))

        output_template = (
            "{name:{name_max_size}} "
            "{destination:{destination_max_size}} "
            "{inverse:{inverse_max_size}} "
            "{type:{type_max_size}} "
            "{through:{through_max_size}}"
        )
        partial_output_template = partial(
            output_template.format,
            name_max_size=name_max_size,
            destination_max_size=destination_max_size,
            inverse_max_size=inverse_max_size,
            type_max_size=type_max_size,
            through_max_size=through_max_size,
        )

        print(
            partial_output_template(
                name=k_name,
                destination=k_destination,
                inverse=k_inverse,
                type=k_type,
                through=k_through,
            )
        )
        print(
            partial_output_template(
                name="=" * name_max_size,
                destination="=" * destination_max_size,
                inverse="=" * inverse_max_size,
                type="=" * type_max_size,
                through="=" * through_max_size,
            )
        )

        legend_output = (
            "name\n"
            "~ <name> - This property is auto generated by Django for access to the set of relationships\n"
            "\n"
            "type\n"
            "<type> * - this property is defined in the related class as a related_name\n"
        )

        if combined_relationship_list:
            for r in combined_relationship_list:
                print(
                    partial_output_template(
                        name=r[k_name],
                        destination=r[k_destination],
                        inverse=r[k_inverse],
                        type=r[k_type],
                        through=r[k_through],
                    )
                )
            print()
            print(legend_output)
        else:
            print("<None>")

    def print_attributes_and_relationships(self, sort=True, reverse=False):
        print("Attributes")
        print()
        self.print_attributes(sort=sort, reverse=reverse)
        print()
        print("Relationships")
        print()
        self.print_relationships(sort=sort, reverse=reverse)

    @classmethod
    def show_attributes_and_relationships(cls, data_type, sort=True, reverse=False):
        a_object_dom = cls(data_type)
        a_object_dom.print_attributes_and_relationships(sort=sort, reverse=reverse)
