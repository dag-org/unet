import { Aws, aws_codebuild, CfnOutput, Fn, Stack } from "aws-cdk-lib"
import ecr = require("aws-cdk-lib/aws-ecr")
import ecs = require("aws-cdk-lib/aws-ecs")
import iam = require("aws-cdk-lib/aws-iam")
import { IRole } from "aws-cdk-lib/aws-iam"
import { Construct } from "constructs"


interface SweepTaskImageProps {
    dockerRepo: ecr.IRepository
    serviceRole: IRole
}

export class SweepTaskImage extends Construct {

    constructor(scope: Construct, id: string, props: SweepTaskImageProps) {
        super(scope, id)

        let gitHubSource = aws_codebuild.Source.gitHub({
            owner: "dag-org",
            repo: "unet",
            webhook: true,
            webhookFilters: [
                aws_codebuild.FilterGroup
                    .inEventOf(aws_codebuild.EventAction.PUSH)
                    .andCommitMessageIsNot("^.*skip\\-build.*$")
            ]
        })

        let ecrRegistry = Fn.sub("${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com")
        let dockerRepoName = props.dockerRepo.repositoryName.toString()

        let tagCommitEcrBase = "${ecrRegistry}/${dockerRepoName}"
        let tagLatest = "${dockerRepoName}:latest"
        let tagLatestEcr = `\${ecrRegistry}/${tagLatest}`
        let environmentVariables = {
            AWS_REGION: {
                type: aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT,
                value: Aws.REGION
            },
            DOCKER_REPO: {
                type: aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT,
                value: dockerRepoName
            },
            ECR_REGISTRY: {
                type: aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT,
                value: ecrRegistry
            },
            TAG_COMMIT_ECR_BASE: {
                type: aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT,
                value: Fn.sub(tagCommitEcrBase, { ecrRegistry, dockerRepoName })
            },
            TAG_LATEST_ECR: {
                type: aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT,
                value: Fn.sub(tagLatestEcr, { dockerRepoName, ecrRegistry })
            },
            WANDB_API_KEY: {
                type: aws_codebuild.BuildEnvironmentVariableType.SECRETS_MANAGER,
                value: "WandbApiTokenSecret:WandbApiKey"
            }
        }

        let buildSpec = aws_codebuild.BuildSpec.fromObjectToYaml({
            version: "0.2",
            phases: {
                  pre_build: {
                    commands : [
                        "aws ecr get-login-password --region ${AWS_REGION} | "
                        + "docker login --username AWS --password-stdin "
                        + "${ECR_REGISTRY}"
                    ]
                  },
                  build: {
                    commands: [
                        "docker build "
                        + "-f exp/Dockerfile "
                        + "-t ${DOCKER_REPO}:${CODEBUILD_RESOLVED_SOURCE_VERSION} "
                        + "--build-arg WANDB_API_KEY=${WANDB_API_KEY} "
                        + "."
                    ]
                  },
                  post_build: {
                    commands: [
                        "docker tag ${DOCKER_REPO}:${CODEBUILD_RESOLVED_SOURCE_VERSION} ${TAG_COMMIT_ECR_BASE}:${CODEBUILD_RESOLVED_SOURCE_VERSION}",
                        "docker tag ${DOCKER_REPO}:${CODEBUILD_RESOLVED_SOURCE_VERSION} ${TAG_LATEST_ECR}",
                        "docker push ${TAG_COMMIT_ECR_BASE}:${CODEBUILD_RESOLVED_SOURCE_VERSION}",
                        "docker push ${TAG_LATEST_ECR}"
                    ]
                }
            }
        })

        new aws_codebuild.Project(this, "SweepExperimentProject", {
            source: gitHubSource,
            environment: {
                buildImage: aws_codebuild.LinuxBuildImage.STANDARD_4_0,
                computeType: aws_codebuild.ComputeType.SMALL,
                privileged: true,
            },
            environmentVariables: environmentVariables,
            role: props.serviceRole,
            buildSpec: buildSpec,
        })
    }
}
