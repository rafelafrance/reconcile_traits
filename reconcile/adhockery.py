#!/usr/bin/env python3
import argparse
import json
import textwrap
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import reconcile.pylib.darwin_core as dwc
from reconcile.pylib.labels.admin_unit import AdminUnit
from reconcile.pylib.labels.id_number import IdNumber
from reconcile.pylib.labels.job import Job
from reconcile.pylib.labels.locality import Locality
from reconcile.pylib.labels.record_number import RecordNumber
from reconcile.pylib.labels.sex import Sex
from reconcile.pylib.labels.taxon_assoc import TaxonAssociation
from reconcile.pylib.labels.taxon_auth import TaxonAuthority
from reconcile.pylib.labels.taxon_name import TaxonName
from reconcile.pylib.labels.taxon_rank import TaxonRank
from reconcile.pylib.traiter.coordinate_precision import CoordinatePrecision
from reconcile.pylib.traiter.coordinate_uncertainty import CoordinateUncertainty
from reconcile.pylib.traiter.decimal_latitude import DecimalLatitude
from reconcile.pylib.traiter.decimal_longitude import DecimalLongitude
from reconcile.pylib.traiter.event_date import EventDate
from reconcile.pylib.traiter.geodetic_datum import GeodeticDatum
from reconcile.pylib.traiter.habitat import Habitat
from reconcile.pylib.traiter.maximum_elevation import MaximumElevationInMeters
from reconcile.pylib.traiter.minimum_elevation import MinimumElevationInMeters
from reconcile.pylib.traiter.verbatim_coordinates import VerbatimCoordinates
from reconcile.pylib.traiter.verbatim_elevation import VerbatimElevation
from reconcile.pylib.traiter.verbatim_system import VerbatimCoordinateSystem
from reconcile.pylib.util import clean_key

CHOICES = ["count-bad-json", "count-label-problems"]


@dataclass
class Terms:
    path: Path
    missing_file: bool = False
    bad_json: bool = False
    all_terms: list[str] = field(default_factory=list)
    bad_terms: list[str] = field(default_factory=list)
    fixed_terms: list[str] = field(default_factory=list)


def main():
    args = parse_args()

    match args.utility:
        case "count-bad-json":
            count_bad_json(args.llm_dir, args.clean_dir)
        case "count-label-problems":
            count_label_problems(args.llm_dir, args.clean_dir)


def count_label_problems(llm_dir, clean_dir):
    all_terms = defaultdict(Terms)
    for path in llm_dir.glob("*.json"):
        all_terms[path.stem] = Terms(path=path)

    clean_paths = {f.stem: f for f in clean_dir.glob("*.json")}

    for stem, terms in all_terms.items():
        if stem not in clean_paths:
            terms.missing_file = True
            continue

        clean_path = clean_paths[stem]
        with terms.path.open() as llm, clean_path.open() as clean:
            llm_text = llm.read()
            clean_text = clean.read()
            if llm_text != clean_text:
                terms.bad_json = True

        fixable_terms = fixable()

        clean_json = json.loads(clean_text)
        for key in clean_json:
            key = clean_key(key)
            terms.all_terms.append(key)
            if key not in dwc.CORE:
                terms.bad_terms.append(key)
                if key in fixable_terms:
                    terms.fixed_terms.append(key)

    missing_file, bad_json, bad_terms, fixed_terms, both = 0, 0, 0, 0, 0
    term_count, bad_count, fixed_count = 0, 0, 0
    for terms in all_terms.values():
        missing_file += 1 if terms.missing_file else 0
        bad_json += 1 if terms.bad_json else 0
        bad_terms += 1 if terms.bad_terms else 0
        fixed_terms += 1 if terms.fixed_terms else 0
        both += 1 if terms.bad_json and terms.bad_terms else 0
        term_count += len(terms.all_terms)
        bad_count += len(terms.bad_terms)
        fixed_count += len(terms.fixed_terms)

    print(f"total labels {len(all_terms)}")
    print(f"missing json files {missing_file}")
    print(f"bad json files {bad_json}")
    print(f"labels with bad terms {bad_terms}")
    print(f"labels with both bad json and bad term {both}")
    print(f"all terms {term_count}")
    print(f"bad terms {bad_count}")
    print(f"fixed terms {fixed_count}")


def fixable() -> set[str]:  # noqa: PLR0915
    fix = set()

    fix |= set(AdminUnit.country_match)
    fix |= set(AdminUnit.code_match)
    fix |= set(AdminUnit.st_match)
    fix |= set(AdminUnit.co_match)
    fix |= set(AdminUnit.muni_match)
    fix.remove(AdminUnit.country_lb)
    fix.remove(AdminUnit.code_lb)
    fix.remove(AdminUnit.st_lb)
    fix.remove(AdminUnit.co_lb)
    fix.remove(AdminUnit.muni_lb)

    fix |= set(IdNumber.acc_match)
    fix |= set(IdNumber.id_match)
    fix.remove(IdNumber.acc_lb)
    fix.remove(IdNumber.id_lb)

    fix |= set(Job.rec_match)
    fix |= set(Job.id_match)
    fix.remove(Job.rec_lb)
    fix.remove(Job.id_lb)

    fix |= set(Locality.loc_match)
    fix |= set(Locality.rem_match)
    fix |= set(Locality.sub_match)
    fix.remove(Locality.label)

    fix |= set(RecordNumber.aliases)
    fix.remove(RecordNumber.label)

    fix |= set(Sex.aliases)
    fix.remove(Sex.label)

    fix |= set(TaxonAssociation.aliases)
    fix.remove(TaxonAssociation.label)

    fix |= set(TaxonAuthority.aliases)
    fix.remove(TaxonAuthority.label)

    fix |= set(TaxonName.matches[0][1])
    fix |= set(TaxonName.matches[1][1])
    fix.remove(TaxonName.sci_name_lb)
    fix.remove(TaxonName.family_lb)

    fix |= set(TaxonRank.aliases)
    fix.remove(TaxonRank.label)

    fix |= set(CoordinatePrecision.aliases)
    fix.remove(CoordinatePrecision.label)

    fix |= set(CoordinateUncertainty.aliases)
    fix.remove(CoordinateUncertainty.label)

    fix |= set(DecimalLatitude.aliases)
    fix.remove(DecimalLatitude.label)

    fix |= set(DecimalLongitude.aliases)
    fix.remove(DecimalLongitude.label)

    fix |= set(EventDate.aliases)
    fix |= set(EventDate.verbatim_aliases)
    fix.remove(EventDate.label)
    fix.remove(EventDate.verbatim_label)

    fix |= set(GeodeticDatum.aliases)
    fix.remove(GeodeticDatum.label)

    fix |= set(Habitat.aliases)
    fix.remove(Habitat.label)

    fix |= set(MaximumElevationInMeters.aliases)
    fix.remove(MaximumElevationInMeters.label)

    fix |= set(MinimumElevationInMeters.aliases)
    fix.remove(MinimumElevationInMeters.label)

    fix |= set(VerbatimCoordinates.aliases)
    fix.remove(VerbatimCoordinates.label)

    fix |= set(VerbatimElevation.aliases)
    fix.remove(VerbatimElevation.label)

    fix |= set(VerbatimCoordinateSystem.aliases)
    fix.remove(VerbatimCoordinateSystem.label)

    return fix


def count_bad_json(llm_dir, clean_dir):
    llm_json = {f.stem: f for f in llm_dir.glob("*.json")}
    clean_json = {f.stem: f for f in clean_dir.glob("*.json")}

    missing = 0
    same = 0
    differ = 0

    for llm_stem, llm_path in llm_json.items():
        if llm_stem not in clean_json:
            missing += 1
            continue

        clean_path = clean_json[llm_stem]
        with llm_path.open() as llm, clean_path.open() as clean:
            llm_text = llm.read()
            clean_text = clean.read()
            if llm_text == clean_text:
                same += 1
            else:
                differ += 1

    total = missing + same + differ
    print(f"{missing=} {same=} {differ=} {total=}")


def parse_args():
    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        fromfile_prefix_chars="@",
        description=textwrap.dedent(
            """
            These are utilities that try to identify or fix various problems when
            dealing with LLM output.

            - count-bad-json: Count how many LLM JSON files were edited to make them
              usable.
            """
        ),
    )

    arg_parser.add_argument(
        "--utility",
        choices=CHOICES,
        default=CHOICES[0],
    )

    arg_parser.add_argument(
        "--llm-dir",
        type=Path,
        metavar="PATH",
        help="""Contains LLM output that may or may not be in JSON format.""",
    )

    arg_parser.add_argument(
        "--clean-dir",
        type=Path,
        metavar="PATH",
        help="""Contains cleaned LLM output in JSON format.""",
    )

    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main()
