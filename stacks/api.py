from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_apigateway as apigw
)


class ExampleLambdaAPI(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        code = _lambda.Code.from_ecr_image(
            repository=props["repository"]
        )

        # handlers
        fastapi_function = _lambda.Function(
            self, "ExampleFunctions",
            runtime=_lambda.Runtime.FROM_IMAGE,
            code=code,
            handler=_lambda.Handler.FROM_IMAGE, retry_attempts=0,
            timeout=core.Duration.minutes(2),
            function_name="example-function"
        )

        api = apigw.RestApi(
            self, "ExampleAPI",
            rest_api_name="example-api",
            deploy_options=apigw.StageOptions(
                tracing_enabled=True,
                data_trace_enabled=True,
                stage_name="v1"
            )
        )

        # define default responses
        unauthorized_response = apigw.CfnGatewayResponse(
            self, "UnauthorizedResponse",
            response_type='UNAUTHORIZED',
            rest_api_id=api.rest_api_id,
            status_code='401',
            response_parameters={
                'gatewayresponse.header.Access-Control-Allow-Origin': "'*'"
            },
            response_templates={
                'application/json': '{"Message": "Authorizer failed to authenticate user"}'
            }
        )

        missing_authentication_token_response = apigw.CfnGatewayResponse(
            self, "MissingAuthenticationTokenResponse",
            response_type='MISSING_AUTHENTICATION_TOKEN',
            rest_api_id=api.rest_api_id,
            status_code='403',
            response_parameters={
                'gatewayresponse.header.Access-Control-Allow-Origin': "'*'"
            },
            response_templates={
                'application/json': '{"Message": $context.error.messageString}'
            }
        )

        integration_timeout_response = apigw.CfnGatewayResponse(
            self, "IntegrationTimeoutResponse",
            response_type='INTEGRATION_TIMEOUT',
            rest_api_id=api.rest_api_id,
            status_code='504',
            response_parameters={
                'gatewayresponse.header.Access-Control-Allow-Origin': "'*'"
            },
            response_templates={
                'application/json': '{"Message": "Apigateway timed out"}'
            }
        )

        invalid_api_key_response = apigw.CfnGatewayResponse(
            self, "InvalidApiKeyResponse",
            response_type='INVALID_API_KEY',
            rest_api_id=api.rest_api_id,
            status_code='403',
            response_parameters={
                'gatewayresponse.header.Access-Control-Allow-Origin': "'*'"
            },
            response_templates={
                'application/json': '{"Message": "Api key provided not authorized"}'
            }
        )

        default_5xx_response = apigw.CfnGatewayResponse(
            self, "Default5XXResponse",
            response_type='DEFAULT_5XX',
            rest_api_id=api.rest_api_id,
            status_code='500',
            response_parameters={
                'gatewayresponse.header.Access-Control-Allow-Origin': "'*'"
            },
            response_templates={
                'application/json': '{"Message": "Server side error"}'
            }
        )

        bad_request_body_response = apigw.CfnGatewayResponse(
            self, "BadResquestBodyResponse",
            response_type='BAD_REQUEST_BODY',
            rest_api_id=api.rest_api_id,
            status_code='400',
            response_parameters={
                'gatewayresponse.header.Access-Control-Allow-Origin': "'*'"
            },
            response_templates={
                'application/json': '{"Message": "Missing body key-value pair"}'
            }
        )

        bad_request_parameters_response = apigw.CfnGatewayResponse(
            self, "BadResquestParametersResponse",
            response_type='BAD_REQUEST_PARAMETERS',
            rest_api_id=api.rest_api_id,
            status_code='400',
            response_parameters={
                'gatewayresponse.header.Access-Control-Allow-Origin': "'*'"
            },
            response_templates={
                'application/json': '{"Message": "Missing query string parameter key-value pair"}'
            }
        )

        access_denied_response = apigw.CfnGatewayResponse(
            self, "AccessDeniedResponse",
            response_type='ACCESS_DENIED',
            rest_api_id=api.rest_api_id,
            status_code='401',
            response_parameters={
                'gatewayresponse.header.Access-Control-Allow-Origin': "'*'"
            },
            response_templates={
                'application/json': '{"Message": "Authorization denied by AWS Cognito"}'
            }
        )

        # define fastapi resource
        fastapi_integration = apigw.LambdaIntegration(fastapi_function)

        proxy_resource = api.root.add_proxy(
            any_method=True,
            default_integration=fastapi_integration
        )

        self.add_cors_options(proxy_resource)

        self.output_props = props.copy()
        self.output_props['stack_name'] = self.stack_name

    @property
    def outputs(self):
        return self.output_props

    def add_cors_options(self, resource):
        """
        Utility method to add CORS to a Apigateway resource

        Args:
            resource (aws_cdk.aws_apigateway.IResource)
        """
        resource.add_method('OPTIONS', apigw.MockIntegration(
            integration_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'",
                    'method.response.header.Access-Control-Allow-Credentials': "'false'",
                    'method.response.header.Access-Control-Allow-Methods': "'GET,PUT,POST,OPTIONS'"
                }
            }],
            passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_MATCH,
            request_templates={"application/json": "{\"statusCode\":200}"}
        ),
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Headers': True,
                    'method.response.header.Access-Control-Allow-Methods': True,
                    'method.response.header.Access-Control-Allow-Credentials': True,
                    'method.response.header.Access-Control-Allow-Origin': True,
                }
            }
        ],
        )