query cadastro_cliente_asaas verb=POST {
  api_group = "Custom"

  input {
    text nome? filters=trim
    text email? filters=trim
    text cpf? filters=trim
    text telefone? filters=trim
    password senha? {
      sensitive = true
      visibility = "internal"
    }
  
    text cep? filters=trim
    text logradouro? filters=trim
    text numero? filters=trim
    text bairro? filters=trim
    text cidade? filters=trim
    text uf? filters=trim
    text complemento? filters=trim
    text referencia? filters=trim
  }

  stack {
    db.add ENDERECO {
      enforce_hidden_fields = false
      data = {
        logradouro : $input.logradouro
        numero     : $input.numero
        complemento: $input.complemento
        bairro     : $input.bairro
        referencia : $input.referencia
      }
    } as $ENDERECO1
  
    db.add CLIENTE {
      enforce_hidden_fields = false
      data = {
        nome   : $input.nome
        celular: $input.telefone
        cpf    : $input.cpf
      }
    } as $CLIENTE1
  
    api.request {
      url = "https://sandbox.asaas.com/api/v3/customers"
      method = "POST"
      params = {}
        |set:"name":$input.nome
        |set:$input.email:$input.email
        |set:"cpfCnpj":$input.cpf
        |set:"mobilePhone":$input.telefone
        |set:"postalCode":$input.cep
        |set:"address":$input.logradouro
        |set:"addressNumber":$input.numero
        |set:"province":$input.bairro
        |set:"complement":$input.complemento
      headers = {}
        |set:"access_token: ":"$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmZmYWJlMTkyLTRlMTEtNGQ4NS1iOTcyLTBkMDM4ZDhkMjg3Mzo6JGFhY2hfYTY1YjljYzMtYjI1ZS00YjViLTg5YjMtNzJkMzcwODJkZDNi"
        |set:"Content-Type: ":"application/json"
    } as $api1
  
    db.edit CLIENTE {
      field_name = $CLIENTE1.id
      field_value = ""
      enforce_hidden_fields = false
      data = {codigoclienteassas: $api1.result.id}
    } as $CLIENTE2
  
    db.add CARTAOTOKNZD {
      enforce_hidden_fields = false
      data = {codigoclienteassas: $api1.result.id}
    } as $CARTAOTOKNZD1
  }

  response = $ENDERECO1
  guid = "aJdck4KaeP7RguJWQfNqiA5Za1Y"
}