openapi: 3.0.0
info:
  title: Terms and Conditions API
  version: v1
paths:
  /terms/{product_id}:
    get:
      summary: Get full terms and conditions for an account
      parameters:
        - in: path
          name: product_id
          schema:
            type: string
          required: true
          description: Unique identifier of the account
        - in: query
          name: product_id
          schema:
            type: string
          required: false
          description: Optional. Unique identifier of a specific product.
        - in: query
          name: version
          schema:
            type: string
          required: false
          description: Optional. Specific version of the terms and conditions.
      responses:
        '200':
          description: Successful retrieval of terms and conditions
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TermsAndConditions'
        '404':
          description: Account not found

  /terms/{product_id}/effective_date:
    get:
      summary: Get the effective date of the terms and conditions
      parameters:
        - in: path
          name: product_id
          schema:
            type: string
          required: true
          description: Unique identifier of the account
      responses:
        '200':
          description: Successful retrieval of effective date
          content:
            application/json:
              schema:
                type: string
                format: date
        '404':
          description: Account not found

  /terms/{product_id}/applicable_fees:
    get:
      summary: Get the effective date of the terms and conditions
      parameters:
        - in: path
          name: product_id
          schema:
            type: string
          required: true
          description: Unique identifier of the account
      responses:
        '200':
          description: Successful retrieval of effective date
          content:
            application/json:
              schema:
                type: string
                format: date
        '404':
          description: Account not found
          
  /terms/{product_id}/apr:
      get:
        summary: Get the effective date of the terms and conditions
        parameters:
          - in: path
            name: product_id
            schema:
              type: string
            required: true
            description: Unique identifier of the account
        responses:
          '200':
            description: Successful retrieval of effective date
            content:
              application/json:
                schema:
                  type: string
                  format: date
          '404':
            description: Account not found
            
  /terms/{product_id}/agreement_link:
      get:
        summary: Get the agreement link
        parameters:
          - in: path
            name: product_id
            schema:
              type: string
            required: true
            description: Unique identifier of the account
        responses:
          '200':
            description: Successful retrieval of effective date
            content:
              application/json:
                schema:
                  type: string
                  format: date
          '404':
            description: Account not found

components:
  schemas:
    TermsAndConditions:
      type: object
      properties:
        terms_and_conditions:
          type: object
          properties:
            effective_date:
              type: string
              format: date
            applicable_fees:
              type: array
              items:
                $ref: '#/components/schemas/Fee'
            apr:
              type: number
              format: float
            apy:
              type: number
              format: float
            credit_limit:
              type: number
              format: float
            rewards_program:
              type: object
              properties:
                name:
                  type: string
                description:
                  type: string
            overdraft_coverage:
              type: boolean
            arbitration_agreement:
              type: boolean
            agreement_link:
              type: string
              format: url
    Fee:
      type: object
      properties:
        fee_name:
          type: string
        fee_amount:
          type: number
          format: float
        fee_description:
          type: string
