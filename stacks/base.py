from aws_cdk import (
    core,
    aws_ssm as ssm,
    aws_s3 as s3,
    aws_ecr as ecr,
    aws_codebuild as codebuild
)

class Base(core.Stack):
    def __init__(self, app: core.App, id: str, props, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        # pipeline requires versioned bucket
        bucket = s3.Bucket(
            self, "SourceBucket",
            bucket_name=f"{props['namespace'].lower()}-{core.Aws.ACCOUNT_ID}",
            versioned=True,
            removal_policy=core.RemovalPolicy.DESTROY)

        # ssm parameter to get bucket name later
        bucket_param = ssm.StringParameter(
            self, "ParameterB",
            parameter_name=f"{props['namespace']}-bucket",
            string_value=bucket.bucket_name,
            description='cdk pipeline bucket'
        )

        # ecr repo to push docker container into
        repository = ecr.Repository(
            self, "ECR",
            repository_name=f"{props['namespace']}",
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # codebuild project meant to run in pipeline
        cb_docker_build = codebuild.PipelineProject(
            self, "DockerBuild",
            project_name=f"{props['namespace']}-Docker-Build",
            build_spec=codebuild.BuildSpec.from_source_filename(
                filename='buildspec.yml'),
            environment=codebuild.BuildEnvironment(
                privileged=True,
            ),
            # pass the ecr repo uri into the codebuild project so codebuild knows where to push
            environment_variables={
                'ecr': codebuild.BuildEnvironmentVariable(
                    value=repository.repository_uri),
                'tag': codebuild.BuildEnvironmentVariable(
                    value='cdk'),
                'region': codebuild.BuildEnvironmentVariable(
                    value=self.region)
            },
            description='Pipeline for CodeBuild',
            timeout=core.Duration.minutes(60),
        )

        # codebuild iam permissions to read write s3
        bucket.grant_read_write(cb_docker_build)

        # codebuild permissions to interact with ecr
        repository.grant_pull_push(cb_docker_build)

        core.CfnOutput(
            self, "ECRURI",
            description="ECR URI",
            value=repository.repository_uri,
        )
        core.CfnOutput(
            self, "S3Bucket",
            description="S3 Bucket",
            value=bucket.bucket_name
        )

        self.output_props = props.copy()
        self.output_props['bucket']= bucket
        self.output_props['repository'] = repository
        self.output_props['cb_docker_build'] = cb_docker_build

    # pass objects to another stack
    @property
    def outputs(self):
        return self.output_props