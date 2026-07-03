import { jsPDF } from 'jspdf'
import { BorderStyle, Document, Packer, Paragraph, TextRun } from 'docx'
import { saveAs } from 'file-saver'
import type { BusinessReport, Hypothesis } from '@/types'
import {
  formatDate,
  reportFileName,
  riskCategoryLabel,
  riskLevelLabel,
  sourceKindLabel,
} from './format'
const BRAND: [number, number, number] = [33, 69, 224]
const INK: [number, number, number] = [30, 41, 59]
const MUTED: [number, number, number] = [100, 116, 139]

async function ensureFonts(doc: jsPDF) {
  const { dejaVuSansRegular, dejaVuSansBold } = await import('./fonts/dejavu')
  doc.addFileToVFS('DejaVuSans.ttf', dejaVuSansRegular)
  doc.addFont('DejaVuSans.ttf', 'DejaVu', 'normal')
  doc.addFileToVFS('DejaVuSans-Bold.ttf', dejaVuSansBold)
  doc.addFont('DejaVuSans-Bold.ttf', 'DejaVu', 'bold')
}

export async function exportReportToPdf(report: BusinessReport): Promise<void> {
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
    doc.setDrawColor(226, 232, 240)
    doc.setLineWidth(0.3)
    doc.line(marginX, y, pageWidth - marginX, y)
    y += 5
  }

  const sectionTitle = (text: string) => {
    y += 2
    paragraph(text.toUpperCase(), { size: 9, bold: true, color: BRAND, lineHeight: 5, gapAfter: 1.5 })
  }

  paragraph('Фабрика гипотез', { size: 20, bold: true, lineHeight: 9, gapAfter: 1 })
  paragraph('Бизнес-отчёт', { size: 11, color: MUTED, lineHeight: 5, gapAfter: 1 })
  paragraph(`Дата генерации: ${formatDate(report.createdAt)}`, {
    size: 9,
    color: MUTED,
    lineHeight: 5,
    gapAfter: 3,
  })
  rule()

  sectionTitle('Технологическая проблема')
  paragraph(report.problem, { size: 12, bold: true, lineHeight: 6, gapAfter: 3 })

  if (report.constraints.length > 0) {
    sectionTitle('Ограничения')
    for (const c of report.constraints) {
      paragraph(`•  ${c}`, { size: 10, lineHeight: 5.4, indent: 2 })
    }
    y += 3
  }

  sectionTitle('Резюме')
  paragraph(report.summary, { size: 10.5, lineHeight: 5.6, gapAfter: 4 })

  rule()
  sectionTitle(`Гипотезы (${report.hypotheses.length})`)
  y += 1

  report.hypotheses.forEach((h, i) => {
    ensureSpace(28)
    paragraph(`${i + 1}. ${h.title}`, { size: 12.5, bold: true, lineHeight: 6, gapAfter: 1.5 })
    paragraph(`Новизна ${h.novelty}/100     Реализуемость ${h.feasibility}/100     KPI: ${h.kpiImpact}`, {
      size: 9.5,
      color: BRAND,
      lineHeight: 5,
      gapAfter: 2.5,
    })

    const field = (label: string, value: string) => {
      doc.setFont('DejaVu', 'bold')
      doc.setFontSize(10)
      doc.setTextColor(...INK)
      const labelWidth = doc.getTextWidth(label + ' ')
      ensureSpace(5.4)
      doc.text(label, marginX, y)
      doc.setFont('DejaVu', 'normal')
      doc.setTextColor(...MUTED)
      const lines = doc.splitTextToSize(value, contentWidth - labelWidth) as string[]
      lines.forEach((l, idx) => {
        if (idx > 0) ensureSpace(5.4)
        doc.text(l, idx === 0 ? marginX + labelWidth : marginX, y)
        y += 5.4
      })
    }

    field('Обоснование:', h.rationale)
    field('Механизм:', h.mechanism)
    field('Ожидаемая ценность:', h.expectedValue)

    y += 1
    paragraph('Риски', { size: 9, bold: true, color: MUTED, lineHeight: 4.6, gapAfter: 1 })
    for (const r of h.risks) {
      paragraph(`•  ${riskCategoryLabel(r.category)} (${riskLevelLabel(r.level)}): ${r.description}`, {
        size: 9.5,
        lineHeight: 5,
        indent: 2,
      })
    }

    y += 1.5
    paragraph('Источники', { size: 9, bold: true, color: MUTED, lineHeight: 4.6, gapAfter: 1 })
    for (const s of h.sources) {
      paragraph(
        `•  [${sourceKindLabel(s.kind)}] ${s.title}${s.year ? ` (${s.year})` : ''}`,
        { size: 9.5, lineHeight: 5, indent: 2 },
      )
    }

    y += 4
    if (i < report.hypotheses.length - 1) rule()
  })

  doc.save(reportFileName(report.problem, 'pdf'))
}

const FONT = 'Calibri'

function labeled(label: string, value: string) {
  return new Paragraph({
    spacing: { after: 80 },
    children: [
      new TextRun({ text: `${label} `, bold: true, size: 22, font: FONT }),
      new TextRun({ text: value, size: 22, font: FONT }),
    ],
  })
}

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
    children: [
      new TextRun({ text: text.toUpperCase(), bold: true, size: 20, color: '2145E0', font: FONT }),
    ],
  })
}

function hypothesisParagraphs(h: Hypothesis, index: number): Paragraph[] {
  return [
    new Paragraph({
      spacing: { before: 260, after: 60 },
      children: [
        new TextRun({ text: `${index + 1}. ${h.title}`, bold: true, size: 26, color: '1E293B', font: FONT }),
      ],
    }),
    new Paragraph({
      spacing: { after: 120 },
      children: [
        new TextRun({
          text: `Новизна ${h.novelty}/100     Реализуемость ${h.feasibility}/100     KPI: ${h.kpiImpact}`,
          size: 20,
          color: '2145E0',
          font: FONT,
        }),
      ],
    }),
    labeled('Обоснование:', h.rationale),
    labeled('Механизм влияния:', h.mechanism),
    labeled('Ожидаемая ценность:', h.expectedValue),
    new Paragraph({
      spacing: { before: 80, after: 40 },
      children: [new TextRun({ text: 'Риски', bold: true, size: 20, color: '64748B', font: FONT })],
    }),
    ...h.risks.map((r) =>
      bullet(`${riskCategoryLabel(r.category)} (${riskLevelLabel(r.level)}): ${r.description}`),
    ),
    new Paragraph({
      spacing: { before: 80, after: 40 },
      children: [new TextRun({ text: 'Источники', bold: true, size: 20, color: '64748B', font: FONT })],
    }),
    ...h.sources.map((s) =>
      bullet(`[${sourceKindLabel(s.kind)}] ${s.title}${s.year ? ` (${s.year})` : ''}${s.url ? ` — ${s.url}` : ''}`),
    ),
  ]
}

export async function exportReportToDocx(report: BusinessReport): Promise<void> {
  const doc = new Document({
    styles: {
      default: {
        document: { run: { font: FONT, size: 22 } },
      },
    },
    sections: [
      {
        properties: { page: { margin: { top: 1000, bottom: 1000, left: 1000, right: 1000 } } },
        children: [
          new Paragraph({
            spacing: { after: 40 },
            children: [
              new TextRun({ text: 'Фабрика гипотез', bold: true, size: 40, color: '1E293B', font: FONT }),
            ],
          }),
          new Paragraph({
            spacing: { after: 40 },
            children: [new TextRun({ text: 'Бизнес-отчёт', size: 24, color: '64748B', font: FONT })],
          }),
          new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: 'E2E8F0', space: 8 } },
            spacing: { after: 120 },
            children: [
              new TextRun({
                text: `Дата генерации: ${formatDate(report.createdAt)}`,
                size: 20,
                color: '64748B',
                font: FONT,
              }),
            ],
          }),

          sectionHeading('Технологическая проблема'),
          new Paragraph({
            spacing: { after: 120 },
            children: [new TextRun({ text: report.problem, bold: true, size: 24, font: FONT })],
          }),

          sectionHeading('Ограничения'),
          ...report.constraints.map((c) => bullet(c)),

          sectionHeading('Резюме'),
          new Paragraph({
            spacing: { after: 120 },
            children: [new TextRun({ text: report.summary, size: 22, font: FONT })],
          }),

          sectionHeading(`Гипотезы (${report.hypotheses.length})`),
          ...report.hypotheses.flatMap((h, i) => hypothesisParagraphs(h, i)),
        ],
      },
    ],
  })

  const blob = await Packer.toBlob(doc)
  saveAs(blob, reportFileName(report.problem, 'docx'))
}
