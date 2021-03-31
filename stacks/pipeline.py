from aws_cdk import (
    core,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as actions,
)


class Pipeline(core.Stack):
    def __init__(self, app: core.App, id: str, props, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        branch = app.node.try_get_context('branch') or 'main'

        # define codecommit repo
        repo = codecommit.Repository(
            self, "Repository",
            repository_name="example",
            description="Testing CI/CD"
        )

        # define the s3 artifact
        source_output = codepipeline.Artifact(artifact_name='source')

        # define the pipeline
        pipeline = codepipeline.Pipeline(
            self, "Pipeline",
            pipeline_name=f"{props['namespace']}",
            artifact_bucket=props['bucket'],
            stages=[
                codepipeline.StageProps(
                    stage_name='Source',
                    actions=[
                        actions.CodeCommitSourceAction(
                            action_name='Source',
                            output=source_output,
                            repository=repo,
                            branch=branch,
                        ),
                    ]
                ),
                codepipeline.StageProps(
                    stage_name='Build',
                    actions=[
                        actions.CodeBuildAction(
                            action_name='DockerBuildImages',
                            input=source_output,
                            project=props['cb_docker_build'],
                            run_order=1,
                        )
                    ]
                ),
                codepipeline.StageProps(
                    stage_name="Deploy",
                    actions=[
                        actions.CloudFormationCreateUpdateStackAction(
                            action_name="CodeDeployExample",
                            admin_permissions=True,
                            stack_name=props["stack_name"],
                            template_path=source_output.at_path("template.yml"),
                            replace_on_failure=True
                        )
                    ]
                )
            ]

        )
        # give pipeline role read write to the bucket
        props['bucket'].grant_read_write(pipeline.role)

        # cfn output
        core.CfnOutput(
            self, "PipelineOut",
            description="Pipeline",
            value=pipeline.pipeline_name
        )