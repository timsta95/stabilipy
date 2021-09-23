import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from functools import cached_property
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Table, TableStyle, Paragraph
from svglib.svglib import svg2rlg
from PyPDF2 import PdfFileMerger, PdfFileReader
from stabilipy import (
    stability as stab, evaluation as eval, export, dam, settings)

@dataclass
class Report(export.Directory, eval.SortedLevels):
    dam: dam.Dam
    levels: list

    def unlevel(self, nested):
        while isinstance(nested, list) and len(nested) == 1:
            nested = nested[0]
        if isinstance(nested, list):
            return [self.unlevel(item) for item in nested]
        else:
            return nested

    @cached_property
    def rearranged(self):
        stabs = [stab.Stability(self.dam, l, i) for l, i in zip(
            self.sorted_levels, settings.ICE_LOADS)]
        loads, moments = zip(*[(s.loads, s.moment) for s in stabs])
        def ra(j):
            return [list(zip(*i)) for i in j]
        return ra(loads), moments

    @property
    def arms(self):
        loads, moments = self.rearranged
        loads, moments = np.array(loads), np.array(moments)
        return np.divide(
            moments, loads, out=np.zeros_like(moments), where=loads != 0)

    @property
    def level_tables(self):
        l, m = self.rearranged
        a = self.arms
        collected = []
        for name, loads, moments, arms in zip(settings.LEVELS, l, m, a):
            dfs = []
            for load, moment, arm in zip(loads, moments, arms):
                df = pd.DataFrame(
                    list(zip(settings.LOADS, load, arm, moment)),
                    columns=(name, 'F [kN]', 'a [m]', 'M [kNm]'))
                dfs.append(df.round(2))
            collected.append(dfs)
        return self.unlevel([list(zip(*collected))])

    @staticmethod
    def check(values):
        return zip(
            *[(f'{i[3]} {settings.IN} [{i[4]}]', i[5]) if isinstance(
                i[4], str) else (
                    f'{i[3]} >= {round(i[4], 2)}', i[5]) for i in values]
        )

    @property
    def summary_tables(self):
        ok, not_ok = settings.OK, settings.NOT_OK
        ev = eval.Evaluation(self.dam, self.sorted_levels)
        g, v = ev.glidning, ev.velting
        p = int(len(g)/ len(self.levels))
        gl_re, ve_re = zip(*[(g[i::p], v[i::p]) for i in range(0, p)])
        dfs = []
        for gl, ve in zip(gl_re, ve_re):
            columns = [gl[0][2]] + list(settings.LEVELS)
            first_col = (settings.GL, settings.VE, settings.SI)
            levels = [i[1] for i in gl]
            l_idx = [levels.index(i) for i in columns[1:]]
            gl_vals, gl_ok = self.check(gl)
            ve_vals, ve_ok = self.check(ve)
            checked = [
                ok if (
                    i == ok and j == ok
                    ) else not_ok for i, j in zip(gl_ok, ve_ok)]
            data = [(
                gl_vals[l_idx[i]], ve_vals[l_idx[i]], checked[l_idx[i]]
                ) for i in range(len(self.levels))]
            dfs.append(
                pd.DataFrame(
                    list(zip(first_col, *data)), columns=columns).round(2))
        return dfs

    def create_images(self, directory):
        color_dict, symbol_dict = settings.COLOR_DICT, settings.SYMBOL_DICT
        verified_dir = self.verify_directory(directory)
        pillars = self.dam.pillars
        counted = len(pillars)
        paths = []
        for level, name, ice in zip(
            self.sorted_levels, settings.LEVELS, settings.ICE_LOADS):
            segments = stab.Stability(self.dam, level, ice).segments_per_pillar
            for p, segs in zip(pillars, segments):
                #set up figure and axes
                fig, ax = plt.subplots()
                ax.set_aspect('equal', 'datalim')
                #pivot point
                pivot_pt = p.right_contact
                ax.plot(pivot_pt.x, pivot_pt.y, 'o', color = 'black')
                #plot segments
                for seg in segs:
                    if seg.load > 0:
                        #plot polygons
                        if seg.name in color_dict:
                            fc = color_dict[seg.name]
                        else:
                            fc = 'gray'
                        xs, ys = seg.coords
                        ax.fill(xs, ys, fc=fc, ec='black', alpha=0.3)
                        #plot centroids
                        if seg.name in symbol_dict:
                            symbol = symbol_dict[seg.name]
                        else:
                            symbol = 'v'
                        xs, ys = seg.centroid.xy
                        ax.plot(xs, ys, symbol, color='yellow')
                #add title and labels
                ax.set_title(f'{name}: {p.name}')
                ax.set_xlabel('X [m]')
                ax.set_ylabel(settings.Y_LABEL)

                path = f'{verified_dir}/{name}_{p.name}.svg'
                fig.savefig(path, format='svg')
                plt.close(fig)
                paths.append(path)
        return [paths[i::counted] for i in range(counted)]

    def create_report(self, directory):
        ok, not_ok = settings.OK, settings.NOT_OK
        verified_dir = self.verify_directory(directory)
        cwidth = 24
        paths = []
        for summary, level, figs, p in zip(
            self.summary_tables, self.level_tables,
            self.create_images(directory), self.dam.pillars):
            #table style
            t_style = TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                              ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                              ('INNERGRID', (0,0), (-1,-1), 0.25,
                               colors.black)])
            #file paths
            name = list(summary.columns)[0]
            path = f'{verified_dir}/{name}_summary.pdf'
            paths.append(path)
            #create canvas
            layout = A4
            c = canvas.Canvas(path, pagesize=layout)
            width, height = layout
            #print level tables onto canvas
            for idx, l in enumerate(level):
                table = l.to_records(index = False).tolist()
                table.insert(0, list(l.columns))
                t = Table(table, colWidths = cwidth * mm)
                t.setStyle(t_style)
                t.wrapOn(c, width, height)
                t.drawOn(c, 0.1 * width, (0.55 - idx * 0.2) * height)
            #print drawings onto canvas
            for idx, fig in enumerate(figs):
                drawing = svg2rlg(fig)
                sx = sy = 0.4
                drawing.width = drawing.minWidth() * sx
                drawing.height = drawing.height * sy
                drawing.scale(sx, sy)
                drawing.wrapOn(c, width, height)
                drawing.drawOn(c, 0.58 * width, (0.54 - idx * 0.2) * height)
            #print summary table onto canvas
            table = summary.to_records(index = False).tolist()
            table.insert(0, list(summary.columns))
            t = Table(table, colWidths = (cwidth + 10) * mm)
            #cell background colors
            for row, values, in enumerate(table):
                for column, value in enumerate(values):
                    if value == not_ok:
                        t_style.add(
                            'BACKGROUND', (column, row),
                            (column, row), colors.red
                            )
                    if value == ok:
                        t_style.add(
                            'BACKGROUND', (column, row),
                            (column, row), colors.green
                            )
            t.setStyle(t_style)
            #place table on canvas
            t.wrapOn(c, width, height)
            t.drawOn(c, 0.18 * width, 0.75 * height)
            #add title to canvas
            styles = getSampleStyleSheet()    
            ptext = f'{name} {settings.CALC}: {p.dam_type}'
            p = Paragraph(ptext, style = styles['Normal'])
            p.wrapOn(c, 150 * mm, 25 * mm)
            p.drawOn(c, 0.17 * width , 0.84 * height)
            styles.add(ParagraphStyle(name = 'Header',
                                      parent = styles['Heading1'],
                                      alignment = TA_CENTER,
                                      fontSize = 16
                                      ))
            ptext = f'{settings.ANALYSIS}: {name}'
            p = Paragraph(ptext, style = styles['Header'])
            p.wrapOn(c, 150 * mm, 40 * mm)
            p.drawOn(c, 0.17 * width , 0.9 * height)
            #save pdf
            c.save()
            #remove svg file
            for fig in figs:
                os.remove(fig)
        #merge pdfs
        path = f'{verified_dir}/Dam_summary.pdf'
        merger = PdfFileMerger()
        for pdf_path in paths:
            with open(pdf_path, 'rb') as pdf:
                merger.append(PdfFileReader(pdf))
        merger.write(path)
        merger.close()
        #remove single-page pdf
        for pdf_path in paths:
            os.remove(pdf_path)
        print(f'PDFs created and saved in {path}')