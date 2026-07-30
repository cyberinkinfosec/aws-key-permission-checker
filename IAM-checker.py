import boto3
from flask import Flask, render_template_string
from botocore.exceptions import ClientError


# ==========================
# AWS CREDENTIALS CONFIG
# ==========================

AWS_CREDENTIALS = [

    {
        "name": "AWS-ACCOUNT-1",
        "access_key": "",
        "secret_key": "",
        "region": ""
    }

]
# ==========================
# FLASK
# ==========================

app = Flask(__name__)


HTML = """

<!DOCTYPE html>
<html>

<head>

<title>AWS Permission Dashboard</title>

<style>

body {
    font-family: Arial;
    margin: 30px;
    background:#f5f5f5;
}

h1 {
    color:#232f3e;
}

.card {

    background:white;
    padding:20px;
    margin-bottom:25px;
    border-radius:8px;
    box-shadow:0 0 8px #ccc;

}


table {

    width:100%;
    border-collapse:collapse;

}


td,th {

    border:1px solid #ddd;
    padding:8px;
    text-align:left;

}


th {

    background:#232f3e;
    color:white;

}


.warning {

    color:red;
    font-weight:bold;

}


pre {

    white-space:pre-wrap;

}

</style>

</head>


<body>


<h1>AWS Access Key Permission Monitor</h1>


{% for item in results %}


<div class="card">


<h2>
{{item.name}}
</h2>


<table>


<tr>
<th>Region</th>
<td>{{item.region}}</td>
</tr>


<tr>
<th>AWS Account</th>
<td>{{item.account}}</td>
</tr>


<tr>
<th>Identity</th>
<td>{{item.identity}}</td>
</tr>


<tr>
<th>Type</th>
<td>{{item.type}}</td>
</tr>


<tr>
<th>IAM Policies</th>
<td>
<pre>{{item.policies}}</pre>
</td>
</tr>


<tr>
<th>S3 Access</th>
<td>
<pre>{{item.s3}}</pre>
</td>
</tr>


</table>


</div>


{% endfor %}


</body>

</html>

"""


# ==========================
# AWS FUNCTIONS
# ==========================


def create_session(creds):

    return boto3.Session(

        aws_access_key_id=creds["access_key"],

        aws_secret_access_key=creds["secret_key"],

        region_name=creds["region"]

    )



def get_identity(session):

    sts = session.client("sts")

    response = sts.get_caller_identity()


    return response



def get_user_policies(session, identity):


    policies=[]


    iam=session.client("iam")


    arn=identity["Arn"]


    # IAM user

    if ":user/" in arn:


        username=arn.split("/")[-1]


        try:

            response=iam.list_attached_user_policies(
                UserName=username
            )


            for p in response["AttachedPolicies"]:

                policies.append(
                    p["PolicyName"]
                )


        except Exception as e:

            policies.append(
                "Unable to read policies: " + str(e)
            )


    else:

        policies.append(
            "Role detected - use IAM role policy analysis"
        )


    return policies



def check_s3(session):


    s3=session.client("s3")


    result=[]


    try:


        buckets=s3.list_buckets()


        for bucket in buckets["Buckets"]:


            name=bucket["Name"]


            result.append(
                "BUCKET: " + name
            )


            try:


                s3.get_bucket_location(
                    Bucket=name
                )


                result.append(
                    "  Access: Allowed"
                )


            except ClientError:


                result.append(
                    "  Access: Limited"
                )



    except ClientError as e:


        result.append(
            "Cannot list buckets"
        )


        result.append(
            str(e)
        )


    return "\n".join(result)



def scan_account(creds):


    output={

        "name":creds["name"],

        "region":creds["region"],

        "account":"",

        "identity":"",

        "type":"",

        "policies":"",

        "s3":""

    }



    try:


        session=create_session(creds)


        identity=get_identity(session)


        output["account"]=identity["Account"]

        output["identity"]=identity["Arn"]



        if ":user/" in identity["Arn"]:

            output["type"]="IAM User"

        else:

            output["type"]="IAM Role"



        policies=get_user_policies(
            session,
            identity
        )


        output["policies"]="\n".join(
            policies
        )


        output["s3"]=check_s3(
            session
        )



    except Exception as e:


        output["identity"]="ERROR"

        output["s3"]=str(e)



    return output



# ==========================
# WEB ROUTE
# ==========================


@app.route("/")
def home():


    results=[]


    for creds in AWS_CREDENTIALS:


        results.append(
            scan_account(creds)
        )


    return render_template_string(

        HTML,

        results=results

    )



# ==========================
# START
# ==========================


if __name__=="__main__":


    print(
        "Dashboard running:"
    )

    print(
        "http://127.0.0.1:5000"
    )


    app.run(

        host="127.0.0.1",

        port=5000

    )
