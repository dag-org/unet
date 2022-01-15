import { App, Aws, aws_codebuild, CfnOutput, Fn, Stack } from "aws-cdk-lib"
import ecr = require("aws-cdk-lib/aws-ecr")
import iam = require("aws-cdk-lib/aws-iam")

import { SweepTaskImage } from "./src/sweep-image"
import { statements } from "./src/statements"


class Images extends Stack {

    constructor(scope, id, props?) {
        super(scope, id)

        let serviceRole = new iam.Role(this, "CodeBuildProjectServiceRole", {
            assumedBy: new iam.ServicePrincipal("codebuild.amazonaws.com"),
            inlinePolicies: {
                CodebuildPolicy: new iam.PolicyDocument({ statements })
            }
        })

        let sweepTaskDockerRepo = new ecr.Repository(this, "SweepTaskDockerRepository", {
            repositoryName: Fn.join("-", [Aws.STACK_NAME, "sweep"])
        })
        new CfnOutput(this, "SweepTaskDkrRepositoryArn", {
            value: sweepTaskDockerRepo.repositoryArn,
            exportName: Fn.join("-", [Aws.STACK_NAME, "SweepTaskDkrRepositoryArn"])
        })
        new SweepTaskImage(this, "SweepTaskImage", {
            serviceRole, dockerRepo: sweepTaskDockerRepo
        })
    }
}

const app = new App();
new Images(app, `unet-images-${app.node.tryGetContext("env")}`)
