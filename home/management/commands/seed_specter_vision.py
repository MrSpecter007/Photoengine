"""
Seed Specter Vision with example content and placeholder images.

Usage:
    docker compose exec web python manage.py seed_specter_vision
    docker compose exec web python manage.py seed_specter_vision --flush
"""

import datetime
import io
import urllib.request

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from wagtail.models import Locale, Page


PICSUM_BASE = "https://picsum.photos/seed"

# (picsum seed, width, height)  — seeds chosen for dark/moody aesthetic
IMAGE_SPECS = {
    "hero-main":       ("specter-hero",    1920, 1080),
    "leica-study":     ("specter-leica",   1920, 1280),
    "porsche-study":   ("specter-911",     1920, 1280),
    "barbour-study":   ("specter-jacket",  1920, 1280),
    "camera-artifact": ("specter-cam",      900,  900),
    "watch-artifact":  ("specter-watch",    900,  900),
    "glass-artifact":  ("specter-glass",    900,  900),
    "note-film":       ("specter-film",    1920, 1080),
    "note-patina":     ("specter-patina",  1920, 1080),
    "note-objects":    ("specter-obj",     1920, 1080),
    "lab-cover":       ("specter-lab",     1920, 1080),
    "world-cover":     ("specter-world",   1920, 1080),
}


def _fetch(seed, width, height):
    url = f"{PICSUM_BASE}/{seed}/{width}/{height}"
    req = urllib.request.Request(url, headers={"User-Agent": "SpecterVision/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def get_or_create_image(title, spec_key):
    from wagtail.images.models import Image

    existing = Image.objects.filter(title=title).first()
    if existing:
        return existing

    seed, w, h = IMAGE_SPECS[spec_key]
    data = _fetch(seed, w, h)
    img = Image(title=title)
    img.file.save(f"{seed}.jpg", ImageFile(io.BytesIO(data), name=f"{seed}.jpg"))
    img.save()
    return img


class Command(BaseCommand):
    help = "Seed Specter Vision with example studies, artifacts, field notes, and pages."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing Specter Vision pages before re-seeding.",
        )

    def log(self, msg):
        self.stdout.write(f"  {msg}")

    def handle(self, *args, **options):
        from home.models import (
            ArtifactIndexPage,
            ArtifactPage,
            CollaboratePage,
            FieldNotePage,
            FieldNotesIndexPage,
            HomePage,
            LabPage,
            StudyIndexPage,
            StudyPage,
            WorldPage,
        )

        locale = Locale.objects.get(language_code="en")
        homepage = HomePage.objects.filter(locale=locale).first()
        if not homepage:
            self.stderr.write("No English HomePage found — run migrations first.")
            return

        if options["flush"]:
            for model in (
                StudyIndexPage,
                ArtifactIndexPage,
                FieldNotesIndexPage,
                LabPage,
                WorldPage,
                CollaboratePage,
            ):
                model.objects.filter(locale=locale).delete()
            self.stdout.write(self.style.WARNING("Flushed existing Specter Vision pages."))

        # ── Placeholder images ────────────────────────────────────────────────
        self.stdout.write("Fetching placeholder images from picsum.photos …")
        imgs = {}
        image_map = {
            "hero":    ("Specter Vision Hero",        "hero-main"),
            "leica":   ("The Leica M6 Study",         "leica-study"),
            "porsche": ("Porsche 911 Study",           "porsche-study"),
            "barbour": ("Barbour Beaufort Study",      "barbour-study"),
            "camera":  ("Leica M6 TTL Artifact",       "camera-artifact"),
            "watch":   ("Seiko SKX007 Artifact",       "watch-artifact"),
            "glass":   ("Persol 714 Artifact",         "glass-artifact"),
            "film":    ("On Shooting Film — Cover",    "note-film"),
            "patina":  ("The Language of Patina — Cover", "note-patina"),
            "objects": ("Objects Worth Keeping — Cover",  "note-objects"),
            "lab":     ("The Lab Cover",               "lab-cover"),
            "world":   ("World Page Cover",            "world-cover"),
        }
        for key, (title, spec) in image_map.items():
            try:
                imgs[key] = get_or_create_image(title, spec)
                self.log(f"✓  {title}")
            except Exception as exc:
                self.log(f"✗  {title}: {exc}")
                imgs[key] = None

        # ── Homepage ─────────────────────────────────────────────────────────
        self.stdout.write("Updating HomePage …")
        homepage.sv_hero_title = "Specter Vision"
        homepage.sv_hero_subtitle = "Visual studies for a material world."
        homepage.sv_manifesto_text = (
            "Specter Vision is the visual studies archive of the Mr. Specter world — "
            "a cinematic research platform exploring objects, vehicles, people, spaces, "
            "materials, and the culture around them."
        )
        homepage.sv_instagram_url = "https://www.instagram.com/mr.specter007"
        homepage.sv_chez_specter_url = "https://chezspecter.com"
        homepage.sv_specter_parts_url = "https://specterparts.com"
        homepage.sv_cta_label = "Propose a Study"
        if imgs.get("hero"):
            homepage.sv_hero_image = imgs["hero"]
        homepage.save_revision().publish()
        self.log("✓  HomePage")

        # ── Studies ───────────────────────────────────────────────────────────
        self.stdout.write("Creating Studies …")
        study_index = StudyIndexPage.objects.filter(locale=locale).first()
        if not study_index:
            study_index = StudyIndexPage(
                title="Studies",
                slug="studies",
                intro_title="Studies",
                intro_text=(
                    "Visual documents from the Specter Vision archive. "
                    "Each study is a sustained investigation into an object, vehicle, "
                    "or material culture worth understanding."
                ),
                locale=locale,
            )
            homepage.add_child(instance=study_index)
            study_index.save_revision().publish()
            self.log("✓  StudyIndexPage")

        studies_created = []

        if not StudyPage.objects.filter(slug="leica-m6-study", locale=locale).exists():
            s1 = StudyPage(
                title="The Leica M6 Study",
                slug="leica-m6-study",
                subtitle="A philosophical instrument in black chrome.",
                study_type="object",
                date=datetime.date(2026, 1, 15),
                location="Montréal, QC",
                thesis=(
                    "The M6 is not a camera. It is an argument for a certain kind of attention — "
                    "slow, deliberate, and without the comfort of a preview. "
                    "This study examines the object as a philosophical instrument."
                ),
                locale=locale,
            )
            if imgs.get("leica"):
                s1.hero_image = imgs["leica"]
            study_index.add_child(instance=s1)
            s1.save_revision().publish()
            studies_created.append(s1)
            self.log("✓  StudyPage: Leica M6")

        if not StudyPage.objects.filter(slug="porsche-911-doctrine", locale=locale).exists():
            s2 = StudyPage(
                title="Porsche 911 Air-Cooled: A Visual Doctrine",
                slug="porsche-911-doctrine",
                subtitle="There are machines built to move. These are built to mean something.",
                study_type="automotive",
                date=datetime.date(2026, 2, 20),
                location="Quebec, Canada",
                thesis=(
                    "There are machines built to move, and machines built to mean something. "
                    "The air-cooled 911 belongs to the second category — "
                    "a vehicle that carries the weight of its own mythology without collapsing under it."
                ),
                locale=locale,
            )
            if imgs.get("porsche"):
                s2.hero_image = imgs["porsche"]
            study_index.add_child(instance=s2)
            s2.save_revision().publish()
            studies_created.append(s2)
            self.log("✓  StudyPage: Porsche 911")

        if not StudyPage.objects.filter(slug="barbour-beaufort", locale=locale).exists():
            s3 = StudyPage(
                title="The Barbour Beaufort",
                slug="barbour-beaufort",
                subtitle="What happens when a utilitarian garment becomes a cultural artifact.",
                study_type="object",
                date=datetime.date(2026, 3, 8),
                location="Montréal, QC",
                thesis=(
                    "The Beaufort waxed cotton jacket has survived 100 years of reinvention "
                    "by remaining stubbornly itself. "
                    "This study tracks what makes an object worth keeping across generations."
                ),
                locale=locale,
            )
            if imgs.get("barbour"):
                s3.hero_image = imgs["barbour"]
            study_index.add_child(instance=s3)
            s3.save_revision().publish()
            studies_created.append(s3)
            self.log("✓  StudyPage: Barbour Beaufort")

        # ── Artifacts ─────────────────────────────────────────────────────────
        self.stdout.write("Creating Artifacts …")
        artifact_index = ArtifactIndexPage.objects.filter(locale=locale).first()
        if not artifact_index:
            artifact_index = ArtifactIndexPage(
                title="Artifacts",
                slug="artifacts",
                intro_title="Artifacts",
                intro_text=(
                    "Objects selected for the Specter Vision archive. "
                    "Each artifact is chosen for its design integrity, material honesty, "
                    "and capacity to outlast the moment it was made for."
                ),
                locale=locale,
            )
            homepage.add_child(instance=artifact_index)
            artifact_index.save_revision().publish()
            self.log("✓  ArtifactIndexPage")

        artifacts_created = []

        if not ArtifactPage.objects.filter(slug="leica-m6-ttl", locale=locale).exists():
            a1 = ArtifactPage(
                title="Leica M6 TTL",
                slug="leica-m6-ttl",
                artifact_type="product_detail",
                short_caption="The last and most balanced film rangefinder Leica ever made.",
                long_description=(
                    "The M6 TTL was produced from 1998 to 2002 — the final iteration "
                    "before digital changed everything. Through-the-lens metering in a "
                    "body that remains the purest expression of the rangefinder format. "
                    "This example is a .72x magnification version in black chrome. "
                    "Shutter speeds accurate. Rangefinder patch bright and clear."
                ),
                date=datetime.date(2023, 6, 1),
                location="Chicago, IL",
                instagram_url="https://www.instagram.com/mr.specter007",
                locale=locale,
            )
            if imgs.get("camera"):
                a1.hero_image = imgs["camera"]
            artifact_index.add_child(instance=a1)
            a1.save_revision().publish()
            artifacts_created.append(a1)
            self.log("✓  ArtifactPage: Leica M6 TTL")

        if not ArtifactPage.objects.filter(slug="seiko-skx007", locale=locale).exists():
            a2 = ArtifactPage(
                title="Seiko SKX007",
                slug="seiko-skx007",
                artifact_type="object",
                short_caption="The platonic ideal of a tool watch. Discontinued 2019.",
                long_description=(
                    "The SKX007 is accurate, durable, and available to anyone. "
                    "Discontinued in 2019, it has become a touchstone for the watch community — "
                    "proof that value has nothing to do with price. "
                    "Crystal replaced with sapphire aftermarket. "
                    "Movement serviced 2024, timing within factory spec."
                ),
                date=datetime.date(2019, 3, 1),
                location="Japan (grey market)",
                locale=locale,
            )
            if imgs.get("watch"):
                a2.hero_image = imgs["watch"]
            artifact_index.add_child(instance=a2)
            a2.save_revision().publish()
            artifacts_created.append(a2)
            self.log("✓  ArtifactPage: Seiko SKX007")

        if not ArtifactPage.objects.filter(slug="persol-714", locale=locale).exists():
            a3 = ArtifactPage(
                title="Persol 714 Steve McQueen Edition",
                slug="persol-714",
                artifact_type="object",
                short_caption="Conceived in 1967. Barely changed since. McQueen wore them in Le Mans.",
                long_description=(
                    "The 714 is one of the great folding sunglasses designs. "
                    "The frame collapses with a mechanism so satisfying it borders on ritual. "
                    "McQueen wore them in Le Mans (1971) without being precious about it. "
                    "This example is mint, unworn, stored in original case."
                ),
                date=datetime.date(2022, 9, 1),
                location="Milano, Italy",
                instagram_url="https://www.instagram.com/mr.specter007",
                locale=locale,
            )
            if imgs.get("glass"):
                a3.hero_image = imgs["glass"]
            artifact_index.add_child(instance=a3)
            a3.save_revision().publish()
            artifacts_created.append(a3)
            self.log("✓  ArtifactPage: Persol 714")

        # ── Field Notes ───────────────────────────────────────────────────────
        self.stdout.write("Creating Field Notes …")
        field_notes_index = FieldNotesIndexPage.objects.filter(locale=locale).first()
        if not field_notes_index:
            field_notes_index = FieldNotesIndexPage(
                title="Field Notes",
                slug="field-notes",
                intro_title="Field Notes",
                intro_text=(
                    "Writing from inside the practice. Essays, observations, "
                    "and working notes from the Specter Vision archive."
                ),
                locale=locale,
            )
            homepage.add_child(instance=field_notes_index)
            field_notes_index.save_revision().publish()
            self.log("✓  FieldNotesIndexPage")

        if not FieldNotePage.objects.filter(slug="shooting-film-2026", locale=locale).exists():
            fn1 = FieldNotePage(
                title="On Shooting Film in 2026",
                slug="shooting-film-2026",
                subtitle="The argument is not nostalgia.",
                category="visual_culture",
                intro=(
                    "The argument for film photography is not nostalgia. "
                    "It is resistance — to the infinite scroll, to the algorithmic feed, "
                    "to the image that costs nothing and therefore means nothing. "
                    "Film enforces scarcity. Scarcity enforces intention."
                ),
                locale=locale,
            )
            if imgs.get("film"):
                fn1.hero_image = imgs["film"]
            field_notes_index.add_child(instance=fn1)
            fn1.save_revision().publish()
            self.log("✓  FieldNotePage: Shooting Film in 2026")

        if not FieldNotePage.objects.filter(slug="language-of-patina", locale=locale).exists():
            fn2 = FieldNotePage(
                title="The Language of Patina",
                slug="language-of-patina",
                subtitle="Patina is not decay. It is autobiography.",
                category="material_study",
                intro=(
                    "Patina is the accumulated record of how an object has moved through the world. "
                    "An unworn leather strap has no story worth reading. "
                    "A brass lens with brassing has been somewhere and done something. "
                    "This is the difference between an object and an artifact."
                ),
                locale=locale,
            )
            if imgs.get("patina"):
                fn2.hero_image = imgs["patina"]
            field_notes_index.add_child(instance=fn2)
            fn2.save_revision().publish()
            self.log("✓  FieldNotePage: Language of Patina")

        if not FieldNotePage.objects.filter(slug="objects-worth-keeping", locale=locale).exists():
            fn3 = FieldNotePage(
                title="Objects Worth Keeping",
                slug="objects-worth-keeping",
                subtitle="A working set of criteria for what earns a place in the archive.",
                category="research",
                intro=(
                    "Not everything old is worth keeping. "
                    "Not everything new is worth discarding. "
                    "The criteria are harder to articulate than they appear: "
                    "it has something to do with honesty of purpose, "
                    "resistance to obsolescence, and the quality of the silence an object keeps."
                ),
                locale=locale,
            )
            if imgs.get("objects"):
                fn3.hero_image = imgs["objects"]
            field_notes_index.add_child(instance=fn3)
            fn3.save_revision().publish()
            self.log("✓  FieldNotePage: Objects Worth Keeping")

        # ── The Lab ───────────────────────────────────────────────────────────
        self.stdout.write("Creating The Lab …")
        if not LabPage.objects.filter(locale=locale).exists():
            lab = LabPage(
                title="The Lab",
                slug="the-lab",
                intro_title="The Lab",
                intro_text=(
                    "Experiments, visual tests, prototypes, and unfinished research. "
                    "The Lab is where Specter Vision works in the open — "
                    "equipment inventories, process notes, and studies in progress."
                ),
                locale=locale,
            )
            homepage.add_child(instance=lab)
            lab.save_revision().publish()
            self.log("✓  LabPage")

        # ── World ─────────────────────────────────────────────────────────────
        self.stdout.write("Creating World …")
        if not WorldPage.objects.filter(locale=locale).exists():
            world = WorldPage(
                title="The World",
                slug="world",
                hero_title="Mr. Specter World",
                hero_text=(
                    "Mr. Specter is a world of objects, vehicles, tools, images, and systems. "
                    "Chez Specter carries the objects. "
                    "Specter Parts powers the sourcing. "
                    "Specter Vision carries the story."
                ),
                chez_specter_url="https://chezspecter.com",
                specter_parts_url="https://specterparts.com",
                instagram_url="https://www.instagram.com/mr.specter007",
                future_builds_text=(
                    "Specter Builds — documentation of mechanical restoration "
                    "and fabrication projects — is in development. "
                    "The first build is already underway."
                ),
                locale=locale,
            )
            homepage.add_child(instance=world)
            world.save_revision().publish()
            self.log("✓  WorldPage")

        # ── Collaborate ───────────────────────────────────────────────────────
        self.stdout.write("Creating Collaborate …")
        collaborate = CollaboratePage.objects.filter(locale=locale).first()
        if not collaborate:
            collaborate = CollaboratePage(
                title="Collaborate",
                slug="collaborate",
                intro_title="Collaborate",
                intro_text=(
                    "Specter Vision is open to meaningful creative and strategic work. "
                    "Propose a study, commission a visual essay, or initiate a collaboration "
                    "that belongs in this world."
                ),
                success_message=(
                    "Your inquiry has been received. "
                    "We review every proposal carefully. "
                    "You will hear from us within 72 hours."
                ),
                locale=locale,
            )
            homepage.add_child(instance=collaborate)
            collaborate.save_revision().publish()
            self.log("✓  CollaboratePage")

        # Link homepage CTA → Collaborate
        homepage.sv_cta_page = collaborate
        homepage.save_revision().publish()
        self.log("✓  HomePage CTA → Collaborate")

        self.stdout.write(self.style.SUCCESS("\nSpecter Vision seeded successfully."))
        self.stdout.write("→  http://localhost:8080")
        self.stdout.write("→  http://localhost:8080/cms  (Wagtail admin)")
