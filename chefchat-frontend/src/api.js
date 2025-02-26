export const sendAuthenticatedRequest = async (url, method, body, token) => {
  const response = await fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Token ${token}`,
    },
    body: JSON.stringify(body)
  });
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  return response.json();
};
