// Unit test for email validation function
const validateEmail = (email) => {
  const atIndex = email.indexOf('@');
  const dotIndex = email.lastIndexOf('.');
  return atIndex > 0 && dotIndex > atIndex + 1 && dotIndex < email.length - 1;
};

test('valid email returns true', () => {
  expect(validateEmail('test@gmail.com')).toBe(true);
});

test('invalid email without @ returns false', () => {
  expect(validateEmail('testgmail.com')).toBe(false);
});
