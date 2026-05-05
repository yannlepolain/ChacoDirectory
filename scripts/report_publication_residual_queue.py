#!/usr/bin/env python3
"""
Generate a publication-audit residual queue that separates:

1. Profiles already substantially audited in this campaign but still scoring as
   risky because they contain old books/chapters, missing DOIs, or residual
   scholar links.
2. Profiles not yet substantially audited that should be the next candidates.
3. Remaining scholar-link cleanup targets.
4. Under-covered profiles not yet substantially audited.

This avoids looping on the same "top risky" names every round.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"
SCHOLAR_PREFIX = "https://scholar.google.com/scholar?q="

# Profiles already given a substantial publication pass in this audit campaign.
AUDITED = {
    "Adámoli, Jorge",
    "Abt Giubergia, María Magdalena",
    "Aguilar, Ramiro",
    "Aliata, María Soledad",
    "Altrichter, Mariana",
    "Araujo-Murakami, Alejandro",
    "Arenas Rodríguez, Pastor",
    "Arispe, Rosario",
    "Ana María Hilda Foschiatti",
    "Balazote, Alejandro",
    "Banegas, Natalia R.",
    "Barbetta, Pablo Nicolás",
    "Bazoberry Chali, Oscar",
    "Belli, Elena",
    "Biocca, Mercedes",
    "Blaser, Mario",
    "Blendinger, Pedro G.",
    "Boaglio, Gabriel Iván",
    "Boffa, Natalia",
    "Bonetti, Carlos Alberto",
    "Brassiolo, Miguel Marcelo",
    "Braunstein, José Alberto",
    "Buliubasich, Emiliana Catalina",
    "Butsic, Van",
    "Bravo, Sandra",
    "Busscher, Nienke",
    "Bucher, Enrique H.",
    "Caballero-Gini, Andrea",
    "Cacciali, Pier",
    "Camba Sans, Gonzalo Hernán",
    "Cabral, Hugo",
    "Caceres, Daniel Mario",
    "Chacoff, Natacha Paola",
    "Campos Krauer, Juan Manuel",
    "Censabella, Marisa Inés",
    "Camardelli, María Cristina",
    "Camino, Micaela",
    "Cantero, Nicolás",
    "Canova, Paola",
    "Capdevila, Luc",
    "Carpio, María Belén",
    "Cardini, Laura Ana",
    "Céspedes, Gloria",
    "Ceriani Cernadas, César Roberto",
    "Cartes Yegros, José Luis",
    "Carlos Lorenzo Langbehn",
    "Combès, Isabelle",
    "Cosso, Pablo Esteban",
    "Coria, Rubén Darío",
    "Correia, Joel E.",
    "Cortez, Sara",
    "Cuyckens, Griet An Erica",
    "Cuéllar Soto, Erika",
    "Cuellar-Álvarez, Néstor",
    "Córdoba, Gisela Soledad",
    "Da Ponte, Emmanuel",
    "Dasso, María Cristina",
    "Dalla-Corte Caballero, Gabriela",
    "De Egea-Elsam, Juana",
    "De Lannoy, Gabriëlle J. M.",
    "De Marzo, Teresa",
    "Damborsky, Miryam Pieri",
    "Díaz, Sandra Myrna",
    "Díaz Lezcano, Maura Isabel",
    "Domínguez, Diego Ignacio",
    "Ernesto Francisco Viglizzo",
    "Engelman, Juan Manuel",
    "Escalada, Cecilia Soledad",
    "Flores Klarik, Mónica",
    "Gareca, Edgar",
    "Giordano, Mariana Lilian",
    "Giordano, Anthony J.",
    "García, Ernesto Dimas",
    "Gamarra Lezcano, Cynthia Carolina",
    "Ginzburg, Rubén Gabriel",
    "Glauser, Marcos",
    "Gómez, César Abel",
    "Gómez-Valencia, Bibiana",
    "González, Hebe Alicia",
    "Gordillo, Gastón",
    "Gasparri, Néstor Ignacio",
    "Glatzle, Albrecht",
    "Goldfarb, Lucía",
    "Gómez-Lende, Sebastián",
    "Harder Horst, René",
    "Hecht, Ana Carolina",
    "Grünewald, Leif",
    "Guevara, Aranzazú",
    "Guillán, María Isabel",
    "Hirsch, Silvia",
    "Houspanossian, Javier",
    "Iñigo Carrera, Valeria",
    "Ibarra-Polesel, Mario Gabriel",
    "Inguaggiato, Carla",
    "Jara, Cristian Emanuel",
    "Kunst, Carlos",
    "Judith Farberman",
    "Krapovickas, Julieta",
    "Laino, Rafaela",
    "Laino, Luis Domingo",
    "Lamenza, Guillermo Nicolás",
    "Laterra, Pedro",
    "Leavy, Pía",
    "Ledesma, Roxana Ramona",
    "Leoni, María Silvia",
    "Lenton, Diana Isabel",
    "Longhi, Fernando",
    "Lorenzetti, Mariana",
    "Lovino, Miguel Ángel",
    "Maillard, Oswaldo",
    "Magliano, Patricio Nicolás",
    "Magliocca, Nicholas",
    "Mancinelli, Gloria",
    "Matarrese, Marina",
    "Matteucci, Silvia Diana",
    "Medina, Mónica Marisel",
    "Mereles Haydar, María Fátima",
    "Messineo, María Cristina",
    "Montani, Rodrigo",
    "Morello, Jorge H",
    "Musálem, Karim",
    "Navall, Jorge Marcelo",
    "Nori, Javier",
    "Navarro Sánchez, Gonzalo",
    "Nanni, Sofía",
    "Lois, Carla",
    "Oakley, Luis J.",
    "Olmedo, Sofía Irene",
    "Ossola, María Macarena",
    "Orfeo, Oscar",
    "Ortega Insaurralde, Carlos",
    "Paolasso, Pablo",
    "Paz, Raúl Gustavo",
    "Peralta-Rivero, Carmelo",
    "Perez de Molas, Luis",
    "Perret, Myriam Fernanda",
    "Peña-Chocarro, María del Carmen",
    "Pensa, Laura",
    "Pratzer, Marie",
    "Powell, Priscila Ana",
    "Preci, Alberto",
    "Paviolo, Agustín Javier",
    "Pötzschner, Florian",
    "Radovich, Juan Carlos",
    "Renison, Daniel",
    "Richard, Nicolas",
    "Rist, Stephan",
    "Rivas, Federico Fernando",
    "Rousseau, Antoine",
    "Rumiz, Damián I.",
    "Rosso, Laura Liliana",
    "Rojas-Bonzi, Viviana",
    "Salamanca, Carlos",
    "Salas Barboza, Ariela Griselda Judith",
    "Salceda, Susana Alicia",
    "Silvetti, Felícitas",
    "Solís Neffa, Viviana Griselda",
    "Suárez, María Eugenia",
    "Suárez, Mauricio Aníbal",
    "Tamagno, Liliana",
    "Tamburini, Daniela María",
    "Teubal, Miguel",
    "Thompson, Jeffrey J.",
    "Texeira, Marcos",
    "Torrella, Sebastián Andrés",
    "Trinchero, Héctor Hugo",
    "Urdampilleta, Constanza",
    "Urioste, Miguel",
    "Vázquez, Fabricio",
    "Vale, Laura M.",
    "Valenzuela, Cristina Ofelia",
    "Vanacker, Veerle",
    "Vidal-Riveros, Cristina",
    "Velilla Fernández, Marianela",
    "Venencia, Cristian Darío",
    "Verón, Santiago Ramón",
    "Via Do Pico, Gisela Mariel",
    "Virginia Belén Toledo López",
    "Viruel, Emilce",
    "Villarino, Sebastián Horacio",
    "Volante, José Norberto",
    "Weiler, Andrea",
    "Villalba, Laura",
    "de la Cruz, Luis María",
    "Seghezzo, Lucas",
    "Reyero, Alejandra Paola Yanina",
    "Zanardini, José",
    "Zorzoli, Facundo Marcelo",
    "Zurlo, Adriana Alicia",
    "Albó, Xavier",
    "Bebbington, Anthony J.",
    "Breithoff, Esther",
    "Galetto, Leonardo",
    "Gras, Carla",
    "Henderson, James",
    "Kamienkowski, Nicolás Martín",
    "Latrubesse, Edgardo M.",
    "Maertens, Michiel",
    "Martín H. Iriondo",
    "Melina Ayelén Tobías",
    "Merenciano González, Ana María",
    "Saldivar-Bellassai, Silvia",
    "Sartori, Ângela Lúcia Bagnatori",
    "Vincent, Frederike",
}

# Profiles reviewed in this campaign that remain unresolved because no
# defensible official replacement or authorship confirmation was found quickly.
# Keep them out of the "fresh" queue unless we intentionally reopen them.
REVIEWED_UNRESOLVED = {
    "García-Calabrese, Milena",
    "Lapegna, Pablo",
    "Maffei, Leonardo",
}


def score_publication(publication: dict) -> int:
    url = publication.get("url", "") or ""
    doi = publication.get("doi", "") or ""
    score = 0

    if not doi:
        score += 2
    if url.startswith(SCHOLAR_PREFIX):
        score += 3
    elif url.startswith("https://books.google.com/"):
        score += 2
    elif url.startswith("https://www.llibreriapublics.com/"):
        score += 2
    elif url.startswith("https://www.researchgate.net/"):
        score += 2
    elif not doi and not url:
        score += 4

    return score


def domain(url: str) -> str:
    return urlparse(url).netloc.lower() if url else ""


def summarize(researcher: dict) -> dict:
    publications = researcher.get("publications", [])
    scholar = 0
    no_doi = 0
    missing_url = 0
    books = 0
    risk_score = 0
    risky_count = 0

    for publication in publications:
        url = publication.get("url", "") or ""
        doi = publication.get("doi", "") or ""
        if url.startswith(SCHOLAR_PREFIX):
            scholar += 1
        if not doi:
            no_doi += 1
        if not url:
            missing_url += 1
        if domain(url) == "books.google.com":
            books += 1

        score = score_publication(publication)
        if score:
            risk_score += score
            risky_count += 1

    return {
        "name": researcher.get("name", ""),
        "pub_count": len(publications),
        "risk_score": risk_score,
        "risky_count": risky_count,
        "scholar": scholar,
        "no_doi": no_doi,
        "missing_url": missing_url,
        "books": books,
        "seed_total": researcher.get("total_publications_in_seed"),
        "year_range": researcher.get("year_range", ""),
        "webpage": bool((researcher.get("webpage") or "").strip()),
    }


def print_section(title: str, rows: list[dict], formatter) -> None:
    print(f"\n{title}")
    if not rows:
        print("- none")
        return
    for row in rows:
        print(formatter(row))


def fmt_risk(row: dict) -> str:
    flags = []
    if row["scholar"]:
        flags.append(f"scholar={row['scholar']}")
    if row["books"]:
        flags.append(f"books={row['books']}")
    if row["missing_url"]:
        flags.append(f"no_url={row['missing_url']}")
    flags.append(f"no_doi={row['no_doi']}")
    return (
        f"- {row['name']}: risk={row['risk_score']}, risky_pubs={row['risky_count']}, "
        f"pubs={row['pub_count']} [{', '.join(flags)}]"
    )


def fmt_undercovered(row: dict) -> str:
    return (
        f"- {row['name']}: pubs={row['pub_count']}, seed={row['seed_total']}, "
        f"webpage={'yes' if row['webpage'] else 'no'}, year_range={row['year_range'] or '-'}"
    )


def main() -> int:
    researchers = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    rows = [summarize(r) for r in researchers]

    audited_residuals = sorted(
        [r for r in rows if r["name"] in AUDITED and r["risk_score"] > 0],
        key=lambda r: (-r["risk_score"], -r["scholar"], r["name"]),
    )
    reviewed_unresolved = sorted(
        [r for r in rows if r["name"] in REVIEWED_UNRESOLVED and r["risk_score"] > 0],
        key=lambda r: (-r["risk_score"], -r["scholar"], r["name"]),
    )
    fresh_high_risk = sorted(
        [
            r
            for r in rows
            if r["name"] not in AUDITED
            and r["name"] not in REVIEWED_UNRESOLVED
            and r["risk_score"] > 0
        ],
        key=lambda r: (-r["risk_score"], -r["scholar"], r["name"]),
    )
    scholar_cleanup = sorted(
        [r for r in rows if r["scholar"] > 0],
        key=lambda r: (-r["scholar"], -r["risk_score"], r["name"]),
    )
    undercovered_unaudited = sorted(
        [
            r
            for r in rows
            if r["name"] not in AUDITED
            and r["name"] not in REVIEWED_UNRESOLVED
            and r["pub_count"] <= 3
        ],
        key=lambda r: (r["pub_count"], r["seed_total"] is not None, r["name"]),
    )

    print(f"Dataset: {DATA_PATH}")
    print(f"Audited profiles tracked in this campaign: {len(AUDITED)}")
    print(f"Reviewed unresolved profiles tracked in this campaign: {len(REVIEWED_UNRESOLVED)}")
    print(f"Already-audited residuals: {len(audited_residuals)}")
    print(f"Reviewed unresolved residuals: {len(reviewed_unresolved)}")
    print(f"Fresh high-risk profiles: {len(fresh_high_risk)}")
    print(f"Profiles with scholar links remaining: {len(scholar_cleanup)}")
    print(f"Under-covered unaudited profiles (<=3 pubs): {len(undercovered_unaudited)}")

    print_section(
        "A. Already Audited, Still Structurally Risky",
        audited_residuals[:20],
        fmt_risk,
    )
    print_section(
        "B. Reviewed But Unresolved",
        reviewed_unresolved[:20],
        fmt_risk,
    )
    print_section(
        "C. Fresh High-Risk Profiles To Audit Next",
        fresh_high_risk[:20],
        fmt_risk,
    )
    print_section(
        "D. Remaining Scholar-Link Cleanup",
        scholar_cleanup[:25],
        fmt_risk,
    )
    print_section(
        "E. Under-covered, Not Yet Substantially Audited",
        undercovered_unaudited[:30],
        fmt_undercovered,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
