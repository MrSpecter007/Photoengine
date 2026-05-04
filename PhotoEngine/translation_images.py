from django.db import models


class TranslationImageSyncMixin:
    image_sync_source_locale = "en"
    translatable_image_fields = ()
    translatable_orderable_relations = {}

    def capture_translation_image_sync_state(self, include_relations=False):
        if (
            getattr(self, "_skip_translation_image_sync", False)
            or not self.pk
            or getattr(self.locale, "language_code", None) != self.image_sync_source_locale
        ):
            return None

        previous = type(self).objects.get(pk=self.pk)
        state = {
            "image_fields": {
                field_name: getattr(previous, f"{field_name}_id")
                for field_name in self.translatable_image_fields
            },
        }

        if include_relations:
            state["relations"] = {
                relation_name: self.serialize_translation_relation(
                    previous,
                    relation_name,
                    config,
                )
                for relation_name, config in self.translatable_orderable_relations.items()
            }

        return state

    def sync_translated_images(self, previous_state, include_relations=False):
        if previous_state is None:
            return

        translations = list(self.get_translations().specific())
        if not translations:
            return

        self.sync_translated_image_fields(previous_state, translations)

        if include_relations:
            self.sync_translated_orderable_relations(previous_state, translations)

    def sync_translated_image_fields(self, previous_state, translations):
        for field_name in self.translatable_image_fields:
            previous_value = previous_state["image_fields"].get(field_name)
            current_value = getattr(self, f"{field_name}_id")

            if previous_value == current_value:
                continue

            for translation in translations:
                if getattr(translation, f"{field_name}_id") != previous_value:
                    continue

                setattr(translation, f"{field_name}_id", current_value)
                translation._skip_translation_image_sync = True
                translation.save(update_fields=[field_name])

    def sync_translated_orderable_relations(self, previous_state, translations):
        previous_relations = previous_state.get("relations", {})

        for relation_name, config in self.translatable_orderable_relations.items():
            previous_items = previous_relations.get(relation_name, [])
            current_items = self.serialize_translation_relation(
                self,
                relation_name,
                config,
            )

            if self.relation_signature(previous_items, config) == self.relation_signature(
                current_items,
                config,
            ):
                continue

            for translation in translations:
                translation_items = self.serialize_translation_relation(
                    translation,
                    relation_name,
                    config,
                )

                if self.relation_signature(
                    translation_items,
                    config,
                ) != self.relation_signature(previous_items, config):
                    continue

                self.replace_translation_relation_items(
                    translation,
                    relation_name,
                    config,
                    translation_items,
                    current_items,
                )

    def serialize_translation_relation(self, instance, relation_name, config):
        items = []
        relation_manager = getattr(instance, relation_name)
        fields_to_capture = (
            set(config.get("copy_fields", ()))
            | set(config.get("preserve_fields", ()))
            | set(config.get("follow_fields", ()))
        )

        for item in relation_manager.all().order_by("sort_order", "pk"):
            row = {"sort_order": item.sort_order}
            for field_name in fields_to_capture:
                field = item._meta.get_field(field_name)
                if isinstance(field, models.ForeignKey):
                    row[field_name] = getattr(item, f"{field_name}_id")
                else:
                    row[field_name] = getattr(item, field_name)
            items.append(row)

        return items

    def relation_signature(self, items, config):
        follow_fields = config.get("follow_fields") or config.get("copy_fields", ())
        return [tuple(item.get(field_name) for field_name in follow_fields) for item in items]

    def replace_translation_relation_items(
        self,
        translation,
        relation_name,
        config,
        existing_items,
        source_items,
    ):
        relation_manager = getattr(translation, relation_name)
        relation_model = relation_manager.model
        parent_field = config["parent_field"]
        follow_fields = config.get("follow_fields") or config.get("copy_fields", ())
        copy_fields = config.get("copy_fields", ())
        preserve_fields = set(config.get("preserve_fields", ()))

        existing_by_key = {
            tuple(item.get(field_name) for field_name in follow_fields): item
            for item in existing_items
        }

        relation_manager.all().delete()

        new_items = []
        for source_item in source_items:
            key = tuple(source_item.get(field_name) for field_name in follow_fields)
            existing_item = existing_by_key.get(key)

            item_kwargs = {
                parent_field: translation,
                "sort_order": source_item.get("sort_order"),
            }

            for field_name in copy_fields:
                value = source_item.get(field_name)
                if existing_item is not None and field_name in preserve_fields:
                    value = existing_item.get(field_name)

                field = relation_model._meta.get_field(field_name)
                if isinstance(field, models.ForeignKey):
                    item_kwargs[f"{field_name}_id"] = value
                else:
                    item_kwargs[field_name] = value

            new_items.append(relation_model(**item_kwargs))

        if new_items:
            relation_model.objects.bulk_create(new_items)
