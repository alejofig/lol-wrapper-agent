export const askAgent = async (playerId: string, question: string): Promise<string> => {
  // Esta es la URL que has creado
  const apiUrl = "https://crbt0l23k1.execute-api.us-east-1.amazonaws.com/v1/ask-agent";

  try {
    const payload = {
      player_identifier: playerId,
      query: question,
    };

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // Envolvemos el payload dentro de un objeto 'body' que se convierte a string,
      // tal como lo espera la integración por defecto de API Gateway.
      body: JSON.stringify({
        body: JSON.stringify(payload)
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      // Lanza un error con el mensaje del backend si está disponible
      throw new Error(errorData.error || "Hubo un error al contactar al agente.");
    }

    // Primero, parseamos la respuesta de API Gateway
    const responseData = await response.json();
    
    // Luego, parseamos el 'body' que está como string dentro de esa respuesta
    const body = JSON.parse(responseData.body);

    // Finalmente, retornamos la propiedad 'answer' del body interno
    return body.answer;

  } catch (error) {
    console.error("Error al llamar al agente RAG:", error);
    // Devuelve un mensaje de error amigable para el usuario
    return "Lo siento, no pude obtener una respuesta en este momento.";
  }
};
