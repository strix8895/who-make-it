## Premise
Please change config file(samconfig.toml) suited your envrioment. 
- stack_name = "clf stack name"
- s3_bucket = "your bucket name"
- s3_prefix = "your prefix name"
- parameter_overrides = "MyRoleARN=\"arn:aws:iam::123456789123:role/test-role\""

## Build
```
sam build --use-container
```

## Test
```
sam local invoke
```
```
sam local start-lambda
aws lambda invoke --function-name "WhoMakeitFunction" --endpoint-url "http://127.0.0.1:3001" --no-verify-ssl out.txt
```

## Deploy
```
sam deploy --config-file samconfig.toml --config-env default
```