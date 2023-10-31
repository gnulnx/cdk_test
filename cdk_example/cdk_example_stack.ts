import { Stack, App, Duration } from 'aws-cdk-lib';
import { Ec2TaskDefinition, Cluster, ContainerImage, InstanceType, InstanceClass, InstanceSize } from 'aws-cdk-lib/aws-ecs';
import { Queue } from 'aws-cdk-lib/aws-sqs';
import { QueueProcessingEc2Service } from 'aws-cdk-lib/aws-ecs-patterns';
import { Construct } from 'constructs';
import { InstanceType } from 'aws-cdk-lib/aws-ec2';

export class FlaskSqsAppStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);

        // Define an SQS queue
        const queue = new Queue(this, "FlaskSqsQueue", {
            queueName: "FlaskSqsQueue",
            visibilityTimeout: Duration.seconds(300)
        });

        // Define an ECS cluster (where your service will be deployed)
        const cluster = new Cluster(this, "FlaskSqsAppCluster", {
            clusterName: "FlaskSqsAppCluster",
            defaultCloudMapNamespace: { name: "johns-name-space" }
        });

        const taskDefinition = new Ec2TaskDefinition(this, "QueueProcessingTaskDef");
        taskDefinition.addContainer("QueueProcessingContainer", {
            image: ContainerImage.fromRegistry("flask-sqs-app"),
            memoryLimitMiB: 512  // Specify the memory limit in MiB
        });

        cluster.addCapacity("CapacityId", {
            instanceType: new InstanceType(InstanceClass.BURSTABLE2, InstanceSize.MICRO),
            minCapacity: 1,
            maxCapacity: 3
        });

        // Create the ECS Service with the previously built Docker image
        new QueueProcessingEc2Service(this, "FlaskSqsService", {
            cluster: cluster,
            // update this to your Docker image URL
            image: ContainerImage.fromRegistry("740239033577.dkr.ecr.us-east-1.amazonaws.com/flask-sqs-app:latest"),
            minScalingCapacity: 1,
            environment: {
                QUEUE_NAME: queue.queueName
            },
            queue: queue,
            memoryLimitMiB: 512
        });
    }
}

const app = new App();
new FlaskSqsAppStack(app, "FlaskSqsAppStack");
