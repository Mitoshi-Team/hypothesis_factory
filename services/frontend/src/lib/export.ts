import { jsPDF } from 'jspdf'
import { BorderStyle, Document, Packer, Paragraph, TextRun } from 'docx'
import { saveAs } from 'file-saver'
import type { HypothesisResult } from '@/types'
import { t } from '@/lib/lang'
import { CRITERIA_KEYS, criteriaLabel, reportFileName, verdictLabel } from './format'

const ACCENT: [number, number, number] = [46, 107, 240]
const INK: [number, number, number] = [28, 29, 31]
const MUTED: [number, number, number] = [99, 102, 107]

async function ensureFonts(doc: jsPDF) {
  const { dejaVuSansRegular, dejaVuSansBold } = await import('./fonts/dejavu')
  doc.addFileToVFS('DejaVuSans.ttf', dejaVuSansRegular)
  doc.addFont('DejaVuSans.ttf', 'DejaVu', 'normal')
  doc.addFileToVFS('DejaVuSans-Bold.ttf', dejaVuSansBold)
  doc.addFont('DejaVuSans-Bold.ttf', 'DejaVu', 'bold')
}

function scoreLine(r: HypothesisResult): string {
  return CRITERIA_KEYS.map((k) => `${criteriaLabel(k)} ${r.scores[k].toFixed(1)}`).join('     ')
}

export async function exportResultToPdf(result: HypothesisResult): Promise<void> {
  const doc = new jsPDF({ unit: 'mm', format: 'a4' })
  const marginX = 18
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const contentWidth = pageWidth - marginX * 2
  let y = 22

  await ensureFonts(doc)

  const ensureSpace = (needed: number) => {
    if (y + needed > pageHeight - 18) {
      doc.addPage()
      y = 22
    }
  }

  const paragraph = (
    text: string,
    opts: {
      size?: number
      bold?: boolean
      color?: [number, number, number]
      lineHeight?: number
      gapAfter?: number
      indent?: number
    } = {},
  ) => {
    const size = opts.size ?? 10.5
    const lineHeight = opts.lineHeight ?? size * 0.52
    const indent = opts.indent ?? 0
    doc.setFont('DejaVu', opts.bold ? 'bold' : 'normal')
    doc.setFontSize(size)
    doc.setTextColor(...(opts.color ?? INK))
    const lines = doc.splitTextToSize(text, contentWidth - indent) as string[]
    for (const l of lines) {
      ensureSpace(lineHeight)
      doc.text(l, marginX + indent, y)
      y += lineHeight
    }
    y += opts.gapAfter ?? 0
  }

  const rule = () => {
    ensureSpace(4)
    doc.setDrawColor(226, 228, 230)
    doc.setLineWidth(0.3)
    doc.line(marginX, y, pageWidth - marginX, y)
    y += 5
  }

  const sectionTitle = (text: string) => {
    y += 2
    paragraph(text, { size: 9, bold: true, color: ACCENT, lineHeight: 5, gapAfter: 1.5 })
  }

  paragraph(t('doc.appTitle'), { size: 20, bold: true, lineHeight: 9, gapAfter: 1 })
  paragraph(t('doc.reportSubtitle'), { size: 11, color: MUTED, lineHeight: 5, gapAfter: 3 })
  rule()

  paragraph(result.title, { size: 14, bold: true, lineHeight: 7, gapAfter: 2 })
  paragraph(`${scoreLine(result)}     ·     ${verdictLabel(result.verdict)}`, {
    size: 9.5,
    color: ACCENT,
    lineHeight: 5,
    gapAfter: 3,
  })

  sectionTitle(t('result.hypothesisLabel'))
  paragraph(result.hypothesis, { size: 10.5, lineHeight: 5.6, gapAfter: 3 })

  sectionTitle(t('result.expectedEffect'))
  paragraph(result.expectedEffect, { size: 10.5, lineHeight: 5.6, gapAfter: 3 })

  sectionTitle(t('result.risks'))
  for (const r of result.risks) paragraph(`•  ${r}`, { size: 10, lineHeight: 5.4, indent: 2 })
  y += 2

  if (result.suggestions.length > 0) {
    sectionTitle(t('result.nextChecks'))
    for (const s of result.suggestions) paragraph(`•  ${s}`, { size: 10, lineHeight: 5.4, indent: 2 })
    y += 2
  }

  sectionTitle(t('result.sources'))
  for (const s of result.evidenceSources) paragraph(`•  ${s}`, { size: 9.5, lineHeight: 5, indent: 2 })

  doc.save(reportFileName(result.title, 'pdf'))
}

const FONT = 'Calibri'

function bullet(text: string) {
  return new Paragraph({
    bullet: { level: 0 },
    spacing: { after: 40 },
    children: [new TextRun({ text, size: 22, font: FONT })],
  })
}

function sectionHeading(text: string) {
  return new Paragraph({
    spacing: { before: 240, after: 100 },
    children: [new TextRun({ text, bold: true, size: 20, color: '2E6BF0', font: FONT })],
  })
}

export async function exportResultToDocx(result: HypothesisResult): Promise<void> {
  const doc = new Document({
    styles: { default: { document: { run: { font: FONT, size: 22 } } } },
    sections: [
      {
        properties: { page: { margin: { top: 1000, bottom: 1000, left: 1000, right: 1000 } } },
        children: [
          new Paragraph({
            spacing: { after: 40 },
            children: [
              new TextRun({ text: t('doc.appTitle'), bold: true, size: 40, color: '1C1D1F', font: FONT }),
            ],
          }),
          new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: 'E2E4E6', space: 8 } },
            spacing: { after: 160 },
            children: [new TextRun({ text: t('doc.reportSubtitle'), size: 22, color: '63666B', font: FONT })],
          }),

          new Paragraph({
            spacing: { after: 60 },
            children: [new TextRun({ text: result.title, bold: true, size: 28, color: '1C1D1F', font: FONT })],
          }),
          new Paragraph({
            spacing: { after: 140 },
            children: [
              new TextRun({
                text: `${scoreLine(result)}     ·     ${verdictLabel(result.verdict)}`,
                size: 20,
                color: '2E6BF0',
                font: FONT,
              }),
            ],
          }),

          sectionHeading(t('result.hypothesisLabel')),
          new Paragraph({
            spacing: { after: 120 },
            children: [new TextRun({ text: result.hypothesis, size: 22, font: FONT })],
          }),

          sectionHeading(t('result.expectedEffect')),
          new Paragraph({
            spacing: { after: 120 },
            children: [new TextRun({ text: result.expectedEffect, size: 22, font: FONT })],
          }),

          sectionHeading(t('result.risks')),
          ...result.risks.map(bullet),

          ...(result.suggestions.length > 0
            ? [sectionHeading(t('result.nextChecks')), ...result.suggestions.map(bullet)]
            : []),

          sectionHeading(t('result.sources')),
          ...result.evidenceSources.map(bullet),
        ],
      },
    ],
  })

  const blob = await Packer.toBlob(doc)
  saveAs(blob, reportFileName(result.title, 'docx'))
}
