"""Source literal quotes must not discard measurements or their exclusion flags."""
from pathlib import Path
import unittest

from yeast.activator.measurements import extract_measurements
from yeast.activator.panels import PANELS
from yeast.activator.source import cell_coordinates, parse_cell, read_sheet


class ActivatorSourceParsingTests(unittest.TestCase):
    def test_starred_curly_quote_values_retain_signed_measurements(self):
        for text, number in (("’-0.01842*", -0.01842),
                             ("’-0.01043*", -0.01043),
                             ("‘-0.01571*", -0.01571)):
            with self.subTest(text=text):
                self.assertEqual(parse_cell(text), (number, True))

    def test_single_literal_prefix_supports_numeric_source_formats(self):
        for text, result in (("'2.5", (2.5, False)),
                             (" ‘1e-3* ", (.001, True)),
                             ("’RPU=0.25", (.25, False)),
                             ("RPU=0.25*", (.25, True)),
                             (-.01, (-.01, False)),
                             (0, (0., False))):
            with self.subTest(text=text):
                self.assertEqual(parse_cell(text), result)

    def test_literal_prefix_does_not_hide_malformed_or_nonfinite_values(self):
        for text in ("’invalid*", "''1.2*", "’NaN*", "'inf*", "1.2'*"):
            with self.subTest(text=text):
                self.assertEqual(parse_cell(text), (None, True))
        self.assertEqual(parse_cell(True), (None, False))
        self.assertEqual(parse_cell(None), (None, False))

    def test_original_hkci_panel_extracts_all_three_cells_with_star_exclusion(self):
        workbook = Path(__file__).resolve().parents[1] / 'data/Source data.xlsx'
        source, green = read_sheet(workbook)
        panel = next(p for p in PANELS if p.panel_id == 'SN9-P2-C')
        try:
            rows = extract_measurements(source['values'], green, panels=[panel])
        except ValueError as error:
            self.fail(f'Original HKCI panel must parse its quoted numeric cells: {error}')
        for cell, text, value in (("AJ48", "’-0.01842*", -.01842),
                                  ("AG49", "’-0.01043*", -.01043),
                                  ("AG50", "‘-0.01571*", -.01571)):
            with self.subTest(cell=cell):
                matches = [row for row in rows if row['source_cell'] == cell]
                self.assertEqual(len(matches), 1)
                row = matches[0]
                self.assertEqual(row['response_rpu'], value)
                self.assertTrue(row['starred_in_workbook'])
                self.assertFalse(row['included_primary'])
                self.assertFalse(row['included_green_exclusion_sensitivity'])
                r, c = cell_coordinates(cell)
                self.assertEqual(source['values'][r][c], text)


if __name__ == '__main__':
    unittest.main()
