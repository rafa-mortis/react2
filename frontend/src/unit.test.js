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
