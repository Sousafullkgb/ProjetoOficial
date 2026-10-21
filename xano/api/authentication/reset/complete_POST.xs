// Validate a one-time password reset link and update the account password.
query "reset/complete" verb=POST {
  api_group = "Authentication"

  input {
    text magic_token filters=trim
    email email filters=trim|lower
    text password filters=trim|min:8
    text confirm_password filters=trim
  }

  stack {
    precondition ($input.password == $input.confirm_password) {
      error = "Passwords do not match."
    }

    db.get user {
      field_name = "email"
      field_value = $input.email
      output = [
        "id"
        "account_id"
        "password_reset.token"
        "password_reset.expiration"
        "password_reset.used"
      ]
    } as $user

    precondition ($user != null) {
      error_type = "unauthorized"
      error = "Invalid or expired password reset link."
    }

    security.check_password {
      text_password = $input.magic_token
      hash_password = $user.password_reset.token
    } as $valid_token

    precondition ($valid_token) {
      error_type = "unauthorized"
      error = "Invalid or expired password reset link."
    }

    precondition ($user.password_reset.expiration > now) {
      error_type = "unauthorized"
      error = "Invalid or expired password reset link."
    }

    precondition ($user.password_reset.used == false) {
      error_type = "unauthorized"
      error = "Invalid or expired password reset link."
    }

    db.edit user {
      field_name = "id"
      field_value = $user.id
      enforce_hidden_fields = false
      data = {
        password: $input.password
        password_reset: {
          token     : $user.password_reset.token
          expiration: $user.password_reset.expiration
          used      : true
        }
      }
    } as $updated_user

    function.run "Getting Started Template/create_event_log" {
      input = {
        user_id   : $user.id
        account_id: $user.account_id
        action    : "reset_password"
        metadata  : {}
      }
    } as $event_log
  }

  response = {message: "Password updated."}
  tags = ["xano:quick-start"]
}
