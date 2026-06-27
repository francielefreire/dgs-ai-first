import { z } from 'zod';

export const structuredOutputSchema = z
  .object({
    answer: z.string().trim().min(1),
    source_document: z.string().trim().min(1),
    confidence_score: z.number().min(0).max(1),
  })
  .strict();

export type StructuredOutput = z.infer<typeof structuredOutputSchema>;

const SAFE_FALLBACK_RESPONSE: StructuredOutput = {
  answer:
    'Não foi possível validar a resposta com segurança. Consulte o supervisor ou a documentação oficial da NovaTech.',
  source_document: 'POL-001-politica-devolucao.md',
  confidence_score: 0,
};

const normalize = (text: string): string =>
  text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase();

const includesDangerousCargoAndReturn = (answer: string): boolean => {
  const normalizedAnswer = normalize(answer);
  const mentionsDangerousCargo =
    normalizedAnswer.includes('carga perigosa') ||
    normalizedAnswer.includes('cargas perigosas');
  const mentionsReturn =
    normalizedAnswer.includes('devolucao') ||
    normalizedAnswer.includes('devolucoes') ||
    normalizedAnswer.includes('devolver') ||
    normalizedAnswer.includes('devolvida') ||
    normalizedAnswer.includes('devolvidas');

  return mentionsDangerousCargo && mentionsReturn;
};

const containsRequiredDenial = (answer: string): boolean => {
  const normalizedAnswer = normalize(answer);
  return (
    normalizedAnswer.includes('nao pode') ||
    normalizedAnswer.includes('nao podem') ||
    normalizedAnswer.includes('nao e permitido') ||
    normalizedAnswer.includes('nao e possivel') ||
    normalizedAnswer.includes('nao sao passiveis de devolucao') ||
    normalizedAnswer.includes('devolucao nao se aplica') ||
    normalizedAnswer.includes('nao ha devolucao') ||
    normalizedAnswer.includes('sem devolucao') ||
    normalizedAnswer.includes('proibido') ||
    normalizedAnswer.includes('nao permitido')
  );
};

const containsAffirmationThatReturnIsPossible = (answer: string): boolean => {
  const normalizedAnswer = normalize(answer);
  const positiveSignals = [
    'pode devolver',
    'podem devolver',
    'e possivel devolver',
    'devolucao pode ser realizada',
    'devolucao e permitida',
    'devolucao permitida',
    'devolucao e possivel',
    'devolucao possivel',
  ];

  const negativeSignals = [
    'nao pode devolver',
    'nao podem devolver',
    'nao e possivel devolver',
    'devolucao nao pode ser realizada',
    'devolucao nao e permitida',
    'devolucao nao permitida',
    'devolucao nao e possivel',
    'devolucao nao possivel',
  ];

  const hasPositiveSignal = positiveSignals.some((signal) =>
    normalizedAnswer.includes(signal)
  );
  const hasNegativeSignal = negativeSignals.some((signal) =>
    normalizedAnswer.includes(signal)
  );

  return hasPositiveSignal && !hasNegativeSignal;
};

const parseModelOutput = (modelOutput: unknown): unknown => {
  if (typeof modelOutput !== 'string') {
    return modelOutput;
  }

  try {
    return JSON.parse(modelOutput);
  } catch {
    console.warn('[response-validator] Resposta rejeitada: JSON inválido.');
    return null;
  }
};

export const validateAssistantResponse = (
  modelOutput: unknown
): StructuredOutput => {
  const parsedOutput = parseModelOutput(modelOutput);
  const validationResult = structuredOutputSchema.safeParse(parsedOutput);

  if (!validationResult.success) {
    console.warn(
      '[response-validator] Resposta rejeitada: schema inválido.',
      validationResult.error.flatten()
    );
    return SAFE_FALLBACK_RESPONSE;
  }

  const response = validationResult.data;

  if (!response.source_document.trim()) {
    console.warn(
      '[response-validator] Resposta rejeitada: source_document ausente.'
    );
    return SAFE_FALLBACK_RESPONSE;
  }

  if (includesDangerousCargoAndReturn(response.answer)) {
    const hasDenial = containsRequiredDenial(response.answer);
    const hasImproperAffirmation =
      containsAffirmationThatReturnIsPossible(response.answer);

    if (!hasDenial) {
      console.warn(
        '[response-validator] Resposta bloqueada: tema "carga perigosa" + "devolução" sem negativa explícita.'
      );
      return SAFE_FALLBACK_RESPONSE;
    }

    if (hasImproperAffirmation) {
      console.warn(
        '[response-validator] Resposta bloqueada: afirmação de devolução possível para carga perigosa.'
      );
      return SAFE_FALLBACK_RESPONSE;
    }
  }

  return response;
};
