import os
from math import cos, sin, radians

import json
import tkinter as tk
import lxml.etree as et

from AppearanceForm import AppearanceForm
from LanguageForm import LanguageForm
from StatsForm import StatsForm
from SaveButton import SaveButton


class StandMaker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.resizable(False, False)
        
        # TODO: default translation is the first one supplied?
        with open(os.path.join('data', 'translations.json'), encoding='utf-8') as f:
            self.translations = json.load(f)
        language = next(iter(self.translations))
        
        self.title(self.translations[language]['window_title'])
        
        self.appearance_form = AppearanceForm(self, self.translations[language])
        self.stats_form = StatsForm(self, self.translations[language])
        self.language_form = LanguageForm(self, self.translations, language)
        self.save_button = SaveButton(self, text=self.translations[language]['save_button'])

        self.appearance_form.contour.add_observer(self.save_button)
        self.appearance_form.poly_fill.add_observer(self.save_button)
        self.appearance_form.poly_stroke.add_observer(self.save_button)
        
        self.stats_form.pack(side=tk.LEFT)
        self.language_form.pack(fill='both', expand=True)
        self.appearance_form.pack(fill='both', expand=True)
        self.save_button.pack(fill='both', expand=True)

    def translate_app(self, lang):
        self.title(self.translations[lang]['window_title'])
        for form in ('appearance', 'stats', 'language'):
            getattr(self, f'{form}_form').translate(self.translations[lang])
        self.save_button.config(text=self.translations[lang]['save_button'])

    def save_to_file(self, filename):
        # Calculate the points of the stat polygon
        CENTER = 64
        DISTANCE_BETWEEN_MARKS = 7
        stat_angles = {
                'power': radians(90),
                'speed': radians(30),
                'range': radians(330),
                'persistence': radians(270),
                'precision': radians(210),
                'development': radians(150)
        }
        stat_marks = {
                stat: getattr(self.stats_form, stat).value
                for stat in stat_angles
        }
        points = [
                (
                    CENTER + int(mark) * DISTANCE_BETWEEN_MARKS * cos(stat_angles[stat]),
                    CENTER - int(mark) * DISTANCE_BETWEEN_MARKS * sin(stat_angles[stat])
                )
                for stat, mark in stat_marks.items()
        ]
        
        # Import base.svg
        svg = et.parse(os.path.join('data', 'base.svg'))
        
        # Draw polygon
        poly_group = svg.find('.//*[@id="polygon"]')
        poly = et.SubElement(
                poly_group,
                'polygon',
                attrib={
                    'points': ' '.join(map(lambda p: f'{p[0]},{p[1]}', points)),
                    'fill': self.appearance_form.poly_fill.color,
                    'stroke': self.appearance_form.poly_stroke.color,
                    'opacity': self.appearance_form.poly_opacity.value
                }
        )
        
        # Replace contour color
        svg.find('.//*[@id="line_color"]').getchildren()[0].attrib['stop-color'] = self.appearance_form.contour.color
        
        svg.write(filename, pretty_print=True)
