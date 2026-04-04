#!/usr/bin/env node

/**
 * beautiful-mermaid render script
 *
 * Renders Mermaid diagrams to SVG, PNG, PDF, or ASCII using beautiful-mermaid.
 *
 * Usage:
 *   node render.mjs --input <file.mmd> --output <file.svg|png|pdf|txt> [options]
 *
 * Options:
 *   --input, -i       Input .mmd file path (or reads from stdin if omitted)
 *   --output, -o      Output file path (extension determines format: .svg, .png, .pdf, .txt)
 *   --format, -f      Force format: svg, png, pdf, ascii (overrides extension detection)
 *   --theme, -t       Theme name (default: zinc-light). See THEMES list below.
 *   --bg              Custom background color (overrides theme)
 *   --fg              Custom foreground color (overrides theme)
 *   --accent          Custom accent color
 *   --transparent     Transparent background (for SVG/PNG)
 *   --scale, -s       PNG scale factor (default: 2 for 2x resolution)
 *   --width, -w       PNG/PDF max width in pixels (default: 1200)
 *   --font            Font family (default: Inter)
 *   --padding         Canvas padding in px (default: 40)
 *   --node-spacing    Horizontal node spacing (default: 24)
 *   --layer-spacing   Vertical layer spacing (default: 40)
 *   --thoroughness    Layout quality 1-7 (default: 3)
 *   --ascii-mode      ASCII box drawing: unicode (default) or ascii
 *   --color-mode      ASCII color: none, auto, ansi16, ansi256, truecolor, html
 *   --help, -h        Show this help
 *
 * Available themes:
 *   default, zinc-light, zinc-dark, tokyo-night, tokyo-night-storm,
 *   tokyo-night-light, catppuccin-mocha, catppuccin-latte, nord, nord-light,
 *   dracula, github-light, github-dark, solarized-light, solarized-dark, one-dark
 *
 * Examples:
 *   node render.mjs -i diagram.mmd -o diagram.svg -t tokyo-night
 *   node render.mjs -i diagram.mmd -o diagram.png -t github-light -s 3
 *   node render.mjs -i diagram.mmd -o diagram.txt -f ascii
 *   echo "graph LR; A-->B" | node render.mjs -o out.svg
 *   node render.mjs -i diagram.mmd -o diagram.pdf -t catppuccin-latte
 */

import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { resolve, extname } from 'node:path'

// --- Argument parsing ---

function parseArgs(argv) {
  const args = {}
  const raw = argv.slice(2)
  for (let i = 0; i < raw.length; i++) {
    const arg = raw[i]
    const next = raw[i + 1]
    switch (arg) {
      case '--input': case '-i': args.input = next; i++; break
      case '--output': case '-o': args.output = next; i++; break
      case '--format': case '-f': args.format = next; i++; break
      case '--theme': case '-t': args.theme = next; i++; break
      case '--bg': args.bg = next; i++; break
      case '--fg': args.fg = next; i++; break
      case '--accent': args.accent = next; i++; break
      case '--transparent': args.transparent = true; break
      case '--scale': case '-s': args.scale = parseFloat(next); i++; break
      case '--width': case '-w': args.width = parseInt(next); i++; break
      case '--font': args.font = next; i++; break
      case '--padding': args.padding = parseInt(next); i++; break
      case '--node-spacing': args.nodeSpacing = parseInt(next); i++; break
      case '--layer-spacing': args.layerSpacing = parseInt(next); i++; break
      case '--thoroughness': args.thoroughness = parseInt(next); i++; break
      case '--ascii-mode': args.asciiMode = next; i++; break
      case '--color-mode': args.colorMode = next; i++; break
      case '--help': case '-h': args.help = true; break
    }
  }
  return args
}

const args = parseArgs(process.argv)

if (args.help) {
  // Print the header comment as help text
  const self = readFileSync(new URL(import.meta.url).pathname, 'utf-8')
  const helpBlock = self.match(/\/\*\*([\s\S]*?)\*\//)?.[1] || ''
  console.log(helpBlock.replace(/^ \* ?/gm, '').trim())
  process.exit(0)
}

// --- Read input ---

let diagram
if (args.input) {
  const inputPath = resolve(args.input)
  if (!existsSync(inputPath)) {
    console.error(`Error: Input file not found: ${inputPath}`)
    process.exit(1)
  }
  diagram = readFileSync(inputPath, 'utf-8')
} else {
  // Read from stdin
  const chunks = []
  process.stdin.setEncoding('utf-8')
  for await (const chunk of process.stdin) {
    chunks.push(chunk)
  }
  diagram = chunks.join('')
}

if (!diagram.trim()) {
  console.error('Error: No diagram input provided. Use --input <file> or pipe via stdin.')
  process.exit(1)
}

// --- Determine output format ---

const outputPath = args.output ? resolve(args.output) : null
let format = args.format
if (!format && outputPath) {
  const ext = extname(outputPath).toLowerCase()
  format = { '.svg': 'svg', '.png': 'png', '.pdf': 'pdf', '.txt': 'ascii' }[ext] || 'svg'
}
format = format || 'svg'

// --- Import beautiful-mermaid ---

const { renderMermaidSVG, renderMermaidASCII, THEMES, DEFAULTS } = await import('beautiful-mermaid')

// --- Build theme/options ---

const themeName = args.theme || 'zinc-light'
let themeColors = THEMES[themeName] || THEMES['zinc-light'] || DEFAULTS

// Apply overrides
if (args.bg) themeColors = { ...themeColors, bg: args.bg }
if (args.fg) themeColors = { ...themeColors, fg: args.fg }
if (args.accent) themeColors = { ...themeColors, accent: args.accent }

const renderOpts = {
  ...themeColors,
  transparent: args.transparent || false,
  font: args.font || 'Inter',
  padding: args.padding ?? 40,
  nodeSpacing: args.nodeSpacing ?? 24,
  layerSpacing: args.layerSpacing ?? 40,
  thoroughness: args.thoroughness ?? 3,
}

// --- Render ---

try {
  if (format === 'ascii') {
    const asciiOpts = {
      useAscii: args.asciiMode === 'ascii',
      colorMode: args.colorMode || 'auto',
    }
    const result = renderMermaidASCII(diagram, asciiOpts)
    if (outputPath) {
      writeFileSync(outputPath, result, 'utf-8')
      console.log(`ASCII diagram written to ${outputPath}`)
    } else {
      process.stdout.write(result + '\n')
    }
  } else if (format === 'svg') {
    const svg = renderMermaidSVG(diagram, renderOpts)
    if (outputPath) {
      writeFileSync(outputPath, svg, 'utf-8')
      console.log(`SVG diagram written to ${outputPath}`)
    } else {
      process.stdout.write(svg)
    }
  } else if (format === 'png') {
    const svg = renderMermaidSVG(diagram, renderOpts)
    const scale = args.scale || 2
    const maxWidth = args.width || 1200

    // Extract viewBox dimensions from SVG
    const vbMatch = svg.match(/viewBox="([^"]*)"/)
    let svgWidth = maxWidth, svgHeight = 800
    if (vbMatch) {
      const parts = vbMatch[1].split(/\s+/).map(Number)
      svgWidth = parts[2] || maxWidth
      svgHeight = parts[3] || 800
    }

    const { default: sharp } = await import('sharp')
    const pngBuffer = await sharp(Buffer.from(svg))
      .resize(Math.round(svgWidth * scale), Math.round(svgHeight * scale), { fit: 'fill' })
      .png()
      .toBuffer()

    if (outputPath) {
      writeFileSync(outputPath, pngBuffer)
      console.log(`PNG diagram (${scale}x) written to ${outputPath}`)
    } else {
      process.stdout.write(pngBuffer)
    }
  } else if (format === 'pdf') {
    const svg = renderMermaidSVG(diagram, renderOpts)

    // Use puppeteer for PDF generation
    let puppeteer
    try {
      puppeteer = await import('puppeteer')
    } catch {
      console.error('Error: puppeteer is required for PDF export. Install it with:')
      console.error('  npm install puppeteer')
      process.exit(1)
    }

    const browser = await puppeteer.default.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    })
    const page = await browser.newPage()

    const bgColor = themeColors.bg || '#ffffff'
    const html = `<!DOCTYPE html>
<html><head><style>
  body { margin: 0; padding: 24px; background: ${bgColor}; display: flex; justify-content: center; }
  svg { max-width: 100%; height: auto; }
</style></head><body>${svg}</body></html>`

    await page.setContent(html, { waitUntil: 'networkidle0' })

    // Get actual content dimensions
    const dims = await page.evaluate(() => {
      const s = document.querySelector('svg')
      return s ? { w: s.getBoundingClientRect().width + 48, h: s.getBoundingClientRect().height + 48 } : { w: 800, h: 600 }
    })

    const pdfBuffer = await page.pdf({
      width: `${Math.ceil(dims.w)}px`,
      height: `${Math.ceil(dims.h)}px`,
      printBackground: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 },
    })

    await browser.close()

    if (outputPath) {
      writeFileSync(outputPath, pdfBuffer)
      console.log(`PDF diagram written to ${outputPath}`)
    } else {
      process.stdout.write(pdfBuffer)
    }
  }
} catch (err) {
  console.error(`Render error: ${err.message}`)
  if (err.stack) console.error(err.stack)
  process.exit(1)
}
