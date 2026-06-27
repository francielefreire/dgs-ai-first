import { describe, expect, it } from 'vitest';
import { validateAssistantResponse } from '../../src/services/response-validator';

describe('validateAssistantResponse', () => {
  it('deve bloquear quando o schema é inválido (sem source_document)', () => {
    const result = validateAssistantResponse({
      answer: 'Prazo de devolução é 7 dias.',
      confidence_score: 0.9,
    });

    expect(result).toEqual({
      answer:
        'Não foi possível validar a resposta com segurança. Consulte o supervisor ou a documentação oficial da NovaTech.',
      source_document: 'POL-001-politica-devolucao.md',
      confidence_score: 0,
    });
  });

  it('deve bloquear quando houver carga perigosa + devolução sem negativa explícita', () => {
    const result = validateAssistantResponse({
      answer:
        'Para carga perigosa, a devolução segue o fluxo padrão com abertura no portal.',
      source_document: 'POL-001',
      confidence_score: 0.8,
    });

    expect(result).toEqual({
      answer:
        'Não foi possível validar a resposta com segurança. Consulte o supervisor ou a documentação oficial da NovaTech.',
      source_document: 'POL-001-politica-devolucao.md',
      confidence_score: 0,
    });
  });

  it('deve bloquear quando afirmar devolução possível para carga perigosa', () => {
    const result = validateAssistantResponse({
      answer:
        'Para carga perigosa, pode devolver desde que haja autorização do supervisor.',
      source_document: 'POL-001',
      confidence_score: 0.82,
    });

    expect(result).toEqual({
      answer:
        'Não foi possível validar a resposta com segurança. Consulte o supervisor ou a documentação oficial da NovaTech.',
      source_document: 'POL-001-politica-devolucao.md',
      confidence_score: 0,
    });
  });
});
