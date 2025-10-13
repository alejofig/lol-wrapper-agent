/**
 * Cliente de AWS AppSync para League of Legends Wrapped
 * Maneja queries, mutations y subscriptions con DynamoDB vía GraphQL
 */

import { Amplify } from 'aws-amplify';
import { generateClient } from 'aws-amplify/api';

// Configurar Amplify con variables de entorno de Astro
Amplify.configure({
  API: {
    GraphQL: {
      endpoint: import.meta.env.PUBLIC_APPSYNC_ENDPOINT,
      region: import.meta.env.PUBLIC_APPSYNC_REGION,
      defaultAuthMode: 'apiKey',
      apiKey: import.meta.env.PUBLIC_APPSYNC_API_KEY
    }
  }
});

const client = generateClient();

// ===== GRAPHQL QUERIES & MUTATIONS =====

export const GET_WRAPPED = `
  query GetWrapped($playerId: ID!, $year: Int!) {
    getWrapped(playerId: $playerId, year: $year) {
      playerId
      year
      status
      gameName
      tagLine
      region
      wrappedData
      requestedAt
      completedAt
      error
    }
  }
`;

export const REQUEST_WRAPPED = `
  mutation RequestWrapped(
    $gameName: String!
    $tagLine: String!
    $region: String!
    $year: Int!
  ) {
    requestWrapped(
      gameName: $gameName
      tagLine: $tagLine
      region: $region
      year: $year
    ) {
      playerId
      status
      gameName
      tagLine
      requestedAt
    }
  }
`;

export const WRAPPED_STATUS_SUBSCRIPTION = `
  subscription OnWrappedStatusChanged($playerId: ID!) {
    onWrappedStatusChanged(playerId: $playerId) {
      playerId
      status
      wrappedData
      completedAt
      error
    }
  }
`;

// ===== TIPOS =====

export type WrappedStatus = 'NOT_FOUND' | 'PROCESSING' | 'COMPLETED' | 'FAILED';

export interface PlayerWrapped {
  playerId: string;
  year: number;
  status: WrappedStatus;
  gameName: string;
  tagLine: string;
  region: string;
  wrappedData?: any;
  requestedAt: string;
  completedAt?: string;
  error?: string;
}

// ===== FUNCIONES HELPERS =====

/**
 * Obtiene el wrapped de un jugador
 */
export async function getWrapped(
  gameName: string,
  tagLine: string,
  year: number = 2025
): Promise<PlayerWrapped> {
  const playerId = `${gameName}#${tagLine}`;

  try {
    const result = await client.graphql({
      query: GET_WRAPPED,
      variables: { playerId, year }
    });

    return result.data.getWrapped;
  } catch (error) {
    console.error('Error getting wrapped:', error);
    throw error;
  }
}

/**
 * Solicita la generación de un wrapped
 */
export async function requestWrapped(
  gameName: string,
  tagLine: string,
  region: string = 'la1',
  year: number = 2025
): Promise<PlayerWrapped> {
  try {
    const result = await client.graphql({
      query: REQUEST_WRAPPED,
      variables: {
        gameName,
        tagLine,
        region,
        year
      }
    });

    return result.data.requestWrapped;
  } catch (error) {
    console.error('Error requesting wrapped:', error);
    throw error;
  }
}

/**
 * Suscribirse a cambios de estado de un wrapped
 * Útil para recibir notificaciones en tiempo real cuando se complete
 */
export function subscribeToWrappedStatus(
  playerId: string,
  callback: (data: PlayerWrapped) => void
) {
  const subscription = client.graphql({
    query: WRAPPED_STATUS_SUBSCRIPTION,
    variables: { playerId }
  }).subscribe({
    next: ({ data }) => {
      if (data?.onWrappedStatusChanged) {
        callback(data.onWrappedStatusChanged);
      }
    },
    error: (error) => {
      console.error('Subscription error:', error);
    }
  });

  return subscription;
}

/**
 * Helper para polling (alternativa a subscriptions)
 * Útil si las subscriptions no funcionan o para debugging
 */
export async function pollWrappedStatus(
  gameName: string,
  tagLine: string,
  onUpdate: (data: PlayerWrapped) => void,
  maxAttempts: number = 30,
  intervalMs: number = 3000
): Promise<void> {
  let attempts = 0;

  const poll = async () => {
    if (attempts >= maxAttempts) {
      onUpdate({
        playerId: `${gameName}#${tagLine}`,
        year: 2025,
        status: 'FAILED',
        gameName,
        tagLine,
        region: 'la1',
        requestedAt: new Date().toISOString(),
        error: 'Timeout: Se agotó el tiempo de espera'
      });
      return;
    }

    try {
      const result = await getWrapped(gameName, tagLine);
      onUpdate(result);

      // Si aún está procesando, seguir polling
      if (result.status === 'PROCESSING') {
        attempts++;
        setTimeout(poll, intervalMs);
      }
    } catch (error) {
      console.error('Polling error:', error);
      attempts++;
      if (attempts < maxAttempts) {
        setTimeout(poll, intervalMs);
      }
    }
  };

  poll();
}


