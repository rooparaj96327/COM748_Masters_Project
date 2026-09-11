import 'dotenv/config'
import { mkdirSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { QdrantClient } from '@qdrant/js-client-rest'

const QDRANT_URL =
  process.env.QDRANT_URL || 'http://localhost:6333'

const QDRANT_API_KEY = process.env.QDRANT_API_KEY

const COLLECTION_NAME =
  process.env.QDRANT_COLLECTION_NAME || 'legal_cases'

const client = new QdrantClient({
  url: QDRANT_URL,
  apiKey: QDRANT_API_KEY,
})

type QdrantPoint = {
  id: string | number
  payload?: Record<string, any>
}

function csvValue(value: unknown): string {
  if (value === null || value === undefined) {
    return '""'
  }

  const text =
    typeof value === 'object'
      ? JSON.stringify(value)
      : String(value)

  return `"${text.replace(/"/g, '""')}"`
}

async function fetchCorpusRegistry(): Promise<QdrantPoint[]> {
  const allPoints: QdrantPoint[] = []

  let offset: string | number | null | undefined = undefined

  while (true) {
    const result = await client.scroll(COLLECTION_NAME, {
      filter: {
        must: [
          {
            key: 'chunk_type',
            match: {
              value: 'metadata_summary',
            },
          },
        ],
      },
      with_payload: true,
      with_vector: false,
      limit: 100,
      ...(offset !== undefined ? { offset } : {}),
    })

    allPoints.push(...(result.points as QdrantPoint[]))

    if (
      result.next_page_offset === null ||
      result.next_page_offset === undefined
    ) {
      break
    }

    offset = result.next_page_offset as string | number
  }

  return allPoints
}

async function main() {
  console.log(`Qdrant URL: ${QDRANT_URL}`)
  console.log(`Collection: ${COLLECTION_NAME}`)
  console.log('Exporting corpus registry...')

  const points = await fetchCorpusRegistry()

  const uniqueCases = new Map<string, Record<string, unknown>>()

  for (const point of points) {
    const payload = point.payload || {}
    const metadata = payload.metadata || {}

    const caseId = String(
      payload.case_id ||
      metadata.case_id ||
      point.id
    )

    if (!uniqueCases.has(caseId)) {
      uniqueCases.set(caseId, {
        qdrant_point_id: String(point.id),
        case_id: caseId,
        title: metadata.title || '',
        neutral_citation:
          metadata.neutral_citation ||
          metadata.neutral_citations ||
          '',
        citation:
          metadata.citation ||
          metadata.citations ||
          '',
        case_year: metadata.case_year || '',
        court: metadata.court || '',
        court_level: metadata.court_level || '',
        jurisdiction: metadata.jurisdiction || '',
        case_category: metadata.case_category || '',
        source_filename: metadata.source_filename || '',
        document_url: metadata.document_url || '',
      })
    }
  }

  const records = Array.from(uniqueCases.values()).sort(
    (a, b) =>
      String(a.title).localeCompare(String(b.title))
  )

  const outputDirectory = join(process.cwd(), 'output')
  mkdirSync(outputDirectory, { recursive: true })

  const date = new Date().toISOString().slice(0, 10)

  const jsonPath = join(
    outputDirectory,
    `qdrant_corpus_registry_${date}.json`
  )

  const csvPath = join(
    outputDirectory,
    `qdrant_corpus_registry_${date}.csv`
  )

  writeFileSync(
    jsonPath,
    JSON.stringify(records, null, 2),
    'utf8'
  )

  const columns = [
    'qdrant_point_id',
    'case_id',
    'title',
    'neutral_citation',
    'citation',
    'case_year',
    'court',
    'court_level',
    'jurisdiction',
    'case_category',
    'source_filename',
    'document_url',
  ]

  const csvLines = [
    columns.map(csvValue).join(','),
    ...records.map(record =>
      columns
        .map(column => csvValue(record[column]))
        .join(',')
    ),
  ]

  writeFileSync(
    csvPath,
    csvLines.join('\n'),
    'utf8'
  )

  console.log('')
  console.log(`Metadata-summary points: ${points.length}`)
  console.log(`Unique corpus cases: ${records.length}`)
  console.log(`JSON saved to: ${jsonPath}`)
  console.log(`CSV saved to: ${csvPath}`)
}

main().catch(error => {
  console.error('Corpus export failed:')
  console.error(error)
  process.exit(1)
})