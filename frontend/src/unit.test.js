// Teste unitário para a função de validação de email
const validateEmail = (email) => {
  const atIndex = email.indexOf('@');
  const dotIndex = email.lastIndexOf('.');
  return atIndex > 0 && dotIndex > atIndex + 1 && dotIndex < email.length - 1;
};

// Teste email válido deve retornar verdadeiro
test('valid email returns true', () => {
  expect(validateEmail('test@gmail.com')).toBe(true);
});

// Teste email inválido sem @ deve retornar falso
test('invalid email without @ returns false', () => {
  expect(validateEmail('testgmail.com')).toBe(false);
});

// Teste mock para email com múltiplos @
test('mock email with multiple @ returns true', () => {
  const mockFn = jest.fn(validateEmail);
  expect(mockFn('test@@gmail.com')).toBe(true);
});

// Teste mock para email sem ponto depois do @
test('mock email without dot after @ returns false', () => {
  const mockFn = jest.fn(validateEmail);
  expect(mockFn('test@gmail')).toBe(false);
});

// Teste mock para email vazio
test('mock empty email returns false', () => {
  const mockFn = jest.fn(validateEmail);
  expect(mockFn('')).toBe(false);
});

// Teste mock para email válido com subdomínio
test('mock valid email with subdomain returns true', () => {
  const mockFn = jest.fn(validateEmail);
  expect(mockFn('user@mail.gmail.com')).toBe(true);
});

// Teste mock para verificar se a função foi chamada
test('mock function call verification', () => {
  const mockFn = jest.fn(validateEmail);
  mockFn('test@gmail.com');
  expect(mockFn).toHaveBeenCalled();
  expect(mockFn).toHaveBeenCalledWith('test@gmail.com');
});
