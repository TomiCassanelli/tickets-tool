'use client'

import { useState, useCallback, useRef, useEffect, memo } from 'react'
import ReactMarkdown from 'react-markdown'

type TicketMarkdown = { markdown: string; metadata: TicketMetadata }

interface TicketMetadata {
  titulo: string
  tipo: string
  prioridad: string
  contexto: string
  criterios_de_aceptacion: string[]
  historia_como: string
  historia_quiero: string
  historia_para: string
}

interface ConversationTurn {
  question: string
  answer: string
}

interface ClarifyState {
  question: string
  needsMore: boolean
  conversationContext: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function TicketDrawer({
  markdown,
  onClose,
  onUpdate,
}: {
  markdown: string
  onClose: () => void
  onUpdate: (md: string) => void
}) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedMarkdown, setEditedMarkdown] = useState(markdown)

  useEffect(() => {
    setEditedMarkdown(markdown)
    setIsEditing(false)
  }, [markdown])

  const handleCopy = async () => {
    await navigator.clipboard.writeText(editedMarkdown)
  }

  const handleSave = () => {
    onUpdate(editedMarkdown)
    setIsEditing(false)
  }

  return (
    <div className="fixed inset-y-0 right-0 w-full md:w-[500px] bg-white shadow-2xl z-50 flex flex-col">
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Ticket Preview</h2>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg active:scale-95 transition-transform"
          >
            Copiar
          </button>
          {isEditing ? (
            <button
              onClick={handleSave}
              className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg active:scale-95 transition-transform"
            >
              Guardar
            </button>
          ) : (
            <button
              onClick={() => setIsEditing(true)}
              className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg active:scale-95 transition-transform"
            >
              Editar
            </button>
          )}
          <button
            onClick={onClose}
            className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg active:scale-95 transition-transform"
          >
            Cerrar
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {isEditing ? (
          <textarea
            value={editedMarkdown}
            onChange={(e) => setEditedMarkdown(e.target.value)}
            className="w-full h-full min-h-[400px] p-3 text-sm font-mono border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        ) : (
          <article className="prose prose-sm max-w-none">
            <ReactMarkdown>{editedMarkdown}</ReactMarkdown>
          </article>
        )}
      </div>
    </div>
  )
}

const ConversationBubble = memo(function ConversationBubble({
  turns,
  currentQuestion,
}: {
  turns: ConversationTurn[]
  currentQuestion: string
}) {
  return (
    <div className="w-full max-w-md mx-auto mb-6 space-y-4">
      {turns.map((turn, index) => (
        <div key={index} className="space-y-2">
          <div className="bg-gray-100 rounded-lg p-3 text-sm text-gray-700">
            <span className="font-medium">Pregunta {index + 1}:</span> {turn.question}
          </div>
          <div className="bg-blue-50 rounded-lg p-3 text-sm text-gray-800 ml-4">
            <span className="font-medium">Tu respuesta:</span> {turn.answer}
          </div>
        </div>
      ))}
      {currentQuestion && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm">
          <span className="font-medium text-amber-800">Nueva pregunta:</span>{' '}
          <span className="text-gray-700">{currentQuestion}</span>
        </div>
      )}
    </div>
  )
})

export default function HomePage() {
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [clarify, setClarify] = useState<ClarifyState | null>(null)
  const [conversationHistory, setConversationHistory] = useState<ConversationTurn[]>([])
  const [ticket, setTicket] = useState<TicketMarkdown | null>(null)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const originalTextRef = useRef<string>('')

  const analyzeRequest = useCallback(async (text: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const res = await fetch(`${API_BASE}/api/analyze-request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: text }),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Error en la solicitud')
      }

      if (data.clarifying_question) {
        setClarify({
          question: data.clarifying_question,
          needsMore: data.needs_more_clarification ?? true,
          conversationContext: data.conversation_context || '',
        })
        originalTextRef.current = text
      } else {
        setClarify(null)
        setConversationHistory([])
        setTicket({ markdown: data.markdown, metadata: data.metadata })
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const continueConversation = useCallback(async (answer: string) => {
    setIsLoading(true)
    setError(null)

    const newHistory = [...conversationHistory, { question: clarify!.question, answer }]
    setConversationHistory(newHistory)

    try {
      const res = await fetch(`${API_BASE}/api/continue-conversation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raw_text: originalTextRef.current,
          conversation_history: newHistory,
        }),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Error en la solicitud')
      }

      if (data.clarifying_question) {
        setClarify({
          question: data.clarifying_question,
          needsMore: data.needs_more_clarification ?? true,
          conversationContext: data.conversation_context || '',
        })
      } else {
        setClarify(null)
        setConversationHistory([])
        setTicket({ markdown: data.markdown, metadata: data.metadata })
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
    } finally {
      setIsLoading(false)
    }
  }, [clarify, conversationHistory])

  const handleSubmit = () => {
    if (!input.trim()) return
    analyzeRequest(input)
    setInput('')
  }

  const handleAnswer = () => {
    if (!input.trim()) return
    continueConversation(input)
    setInput('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (clarify) {
        handleAnswer()
      } else {
        handleSubmit()
      }
    }
  }

  const resetConversation = () => {
    setClarify(null)
    setConversationHistory([])
    setTicket(null)
    setError(null)
  }

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col">
      <div className="flex-1 flex flex-col lg:flex-row">
        <div className="flex-1 flex flex-col justify-center p-4 pb-32 lg:pb-4">
          <div className="w-full max-w-2xl mx-auto">
            <div className="flex items-center justify-between mb-8">
              <h1 className="text-2xl font-bold text-gray-900">Ticket Generator</h1>
              {(clarify || ticket) && (
                <button
                  onClick={resetConversation}
                  className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Nueva conversación
                </button>
              )}
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
                {error}
              </div>
            )}

            {clarify && conversationHistory.length > 0 && (
              <ConversationBubble
                turns={conversationHistory}
                currentQuestion={clarify.question}
              />
            )}

            {clarify && conversationHistory.length === 0 && (
              <div className="w-full max-w-md mx-auto mb-6">
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm">
                  <p className="font-medium text-amber-800 mb-2">
                    El asistente necesita más información:
                  </p>
                  <p className="text-gray-700">{clarify.question}</p>
                </div>
              </div>
            )}

            <div className="w-full max-w-md mx-auto">
              <div className="relative">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={
                    clarify
                      ? 'Responde a la pregunta del asistente...'
                      : 'Describe tu ticket o problema...'
                  }
                  disabled={isLoading}
                  className="w-full p-4 pr-24 text-base border border-gray-300 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[120px] shadow-sm"
                  rows={4}
                />
                <button
                  onClick={clarify ? handleAnswer : handleSubmit}
                  disabled={!input.trim() || isLoading}
                  className="absolute right-3 bottom-3 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-xl disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 transition-all"
                >
                  {isLoading ? '...' : clarify ? 'Responder' : 'Enviar'}
                </button>
              </div>
              <p className="text-xs text-gray-400 text-center mt-2">
                {clarify
                  ? 'Presiona Enter para responder'
                  : 'Presiona Enter para enviar, Shift+Enter para nueva línea'}
              </p>
            </div>
          </div>
        </div>

        {ticket && (
          <TicketDrawer
            markdown={ticket.markdown}
            onClose={() => setTicket(null)}
            onUpdate={(md) => setTicket((prev) => prev ? { ...prev, markdown: md } : null)}
          />
        )}
      </div>
    </main>
  )
}