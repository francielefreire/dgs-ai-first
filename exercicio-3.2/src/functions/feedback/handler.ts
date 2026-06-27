import { app, HttpRequest, HttpResponseInit, InvocationContext } from '@azure/functions';
import { z } from 'zod';
import pino from 'pino';
import { CosmosClient } from '@azure/cosmos';

const logger = pino({ name: 'feedback-handler' });

const feedbackSchema = z
  .object({
    queryId: z.string().trim().min(1),
    rating: z.number().int().min(1).max(5),
    comment: z.string().trim().max(1000).optional(),
    attendantEmail: z.string().email(),
  })
  .strict();

type FeedbackInput = z.infer<typeof feedbackSchema>;

const toPersistedFeedback = (input: FeedbackInput) => ({
  queryId: input.queryId,
  rating: input.rating,
  comment: input.comment ?? null,
  attendantEmail: input.attendantEmail,
  timestamp: new Date().toISOString(),
});

export async function feedbackHandler(
  request: HttpRequest,
  _context: InvocationContext
): Promise<HttpResponseInit> {
  let payload: unknown;

  try {
    payload = await request.json();
  } catch {
    logger.warn('Invalid JSON payload on feedback endpoint');
    return {
      status: 400,
      jsonBody: { error: 'Invalid JSON payload' },
    };
  }

  const parsed = feedbackSchema.safeParse(payload);

  if (!parsed.success) {
    logger.warn(
      {
        issues: parsed.error.issues.map((issue) => ({
          path: issue.path.join('.'),
          code: issue.code,
        })),
      },
      'Feedback payload validation failed'
    );

    return {
      status: 400,
      jsonBody: { error: 'Invalid feedback payload' },
    };
  }

  try {
    const connectionString = process.env.COSMOS_CONNECTION_STRING;

    if (!connectionString) {
      logger.error('Missing COSMOS_CONNECTION_STRING');
      return {
        status: 500,
        jsonBody: { error: 'Service temporarily unavailable' },
      };
    }

    const client = new CosmosClient(connectionString);
    const database = client.database('novatech');
    const container = database.container('feedbacks');

    const feedback = toPersistedFeedback(parsed.data);
    await container.items.create(feedback);

    logger.info(
      {
        queryId: feedback.queryId,
        rating: feedback.rating,
        hasComment: Boolean(feedback.comment),
      },
      'Feedback persisted successfully'
    );

    return {
      status: 200,
      jsonBody: { status: 'ok' },
    };
  } catch (error) {
    logger.error({ err: error }, 'Failed to persist feedback');
    return {
      status: 500,
      jsonBody: { error: 'Internal server error' },
    };
  }
}

app.http('feedback', {
  methods: ['POST'],
  handler: feedbackHandler,
});
