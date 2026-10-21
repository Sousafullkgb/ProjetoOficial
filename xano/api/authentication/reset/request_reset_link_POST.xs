// Request a one-time magic link to reset password by email
query "reset/request-reset-link" verb=POST {
  api_group = "Authentication"

  input {
    email email filters=trim|lower
  }

  stack {
    db.get user {
      field_name = "email"
      field_value = $input.email
      output = ["id", "email"]
    } as $user

    conditional {
      if ($user != null) {
        function.run "Getting Started Template/generate_magic_link" {
          input = {email: $input.email}
        } as $token_and_email

        var $magic_link {
          value = $env.ggreviews_frontend_url ~ "?magic_token=" ~ $token_and_email.token ~ "&email=" ~ ($token_and_email.email|url_encode)
        }

        api.request {
          url = "https://api.sendgrid.com/v3/mail/send"
          method = "POST"
          params = {
            personalizations: [
              {
                to: [{email: $token_and_email.email}]
              }
            ]
            from   : {email: $env.sendgrid_from_email}
            subject: "Redefinição de senha do GGReviews"
            content: [
              {
                type : "text/html"
                value: "<p>Recebemos uma solicitação para redefinir sua senha do GGReviews.</p><p><a href=\"" ~ $var.magic_link ~ "\">Redefinir senha</a></p><p>Se você não solicitou a redefinição, ignore este e-mail.</p>"
              }
            ]
          }
          headers = [
            "Authorization: Bearer " ~ $env.sendgrid_api_key
            "Content-Type: application/json"
          ]
        } as $email_response

        precondition ($email_response.response.status == 202) {
          error = "Unable to send password reset email."
        }
      }
    }
  }

  response = {message: "If an account exists, a reset link has been sent."}

  tags = ["xano:quick-start"]
  guid = "9FLwxi5uOJ24gomL6pqVwy43h78"
}