> "Use Docker!", they said. "It makes everything more secure!", they said.

# Oh dear! Another Docker-related project!? What is it this time?
A few years ago, most of us started to adopt the new hotness, and put everything into docker-containers, 
that wasn't able to run away fast enough. 

Most of those containers have been created once and then have been quickly forgotten - along with the fact, that there's a complete
operating system running inside those containers. And that it needs to receive some updates now and then.

The images that we extend from get updated quite regularly (well, most of them). And there are
important security-fixes among the updates, that we definitely want to have!

But how do we know that? How do we get informed of new updates to adopt, so that we get reminded, 
that using Docker isn't a fire-and-forget process!?
Well, there is no automatic process to this ...or, is it?

This project want's to achieve a somewhat/semi automatic process, to do exactly that - and more!


### Features
* determine the parent image and the last update-date of the used tag
* compare with the latest tag of the image
* trigger the corresponding build-pipeline, if its outdated
* check if the parent image itself is outdated (configurable timeframe)
* send a mail-report with the scan-result

# Limitations and pre-conditions
* Only supports **MS Azure** at the moment (and DockerHub for the parent images of course)

There needs to be:
* a user/token with read-access to all the configured git-repositories and the build-pipelines
* _one_ <code>Dockerfile</code> somewhere in your Repository
  * it must extend a parent image from DockerHub or one of the ACRs that are configured!
* _one_ build-pipeline or rather the corresponding <code>azure-pipelines.yaml</code> in the root of your git-repository
* a variable with the name "imageName" (containing - so "myImageName" would also work) and the value must be the name of the pushed docker-image _without_ the tag! (the value can be enclosed in quotes, but don't have to)
* the target Azure Container Registries (ACR) must have its credentials configured (via env-variable ATM)
* _if_ the Dockerfile uses an <code>ARG</code> (build-variable) for the tag of the parent image, then the <code>azure-pipelines.yaml</code> must contain the real value in a variable "version" (again: containing and with or without quotes)


# Alright, lets do this!
You made sure, that your repository fulfills all those requirements? Great!<br/>
Then open the <code>repos.py</code> file and add a new Block:
<pre>
"unique-key": {
        "name": "should-match-the-git-repo-name",
        "git": "https://ciuser@dev.azure.com/YOUR_COMPANY/YOUR_PROJECT/_git/your-git-repository",
        "acr": "the-acr-your-build-pipeline-pushes-to",
        "build_pipeline": "name-of-the-build-pipeline",
        "project": "YOUR_PROJECT"
}
</pre>
Replace the "unique-key" and all the values and push the changes into a feature-branch.<br/>

### configure it
Next you have to configure some settings. Move or copy the file <code>config.py.tmpl</code> to <code>config.py</code>, 
and open it. Change at least all occurrences of "REPLACE_ME" to fit your environment!


### build it
Use the template of the azure-pipelines.yml to configure and setup a build-pipeline.
You need to configure the name of your ACR.

If you don't have a SonarQube instance connected, just delete those build-steps along with the test-coverage steps!

### run it
If you don't have an Azure KeyVault already: now is the time to create one!
You really want it to store the required credentials in it!!!

Now, create a new Release-Pipeline. 
It doesn't need any artifacts as input, but you might want to setup a "Scheduled release trigger".

* The stage just consists of two tasks. An "Azure Key Vault"-Task, referencing your KeyVault with all the necessary credentials.
* A Docker@V1 Task, to run your image
  * reference the ACR you pushed the image into
  * enter "run" as command
  * enter the proper imagename and tag (e.g. "docker-update-scan:latest")
  * and the most important part: the environment variables - use it to specify the credentials from the KeyVault. For example like this:
  <pre>
    GIT_PASSWORD=$(ciUserGitPassword)
    DEVOPS_PAT=$(pipelineAccessToken)
    ACR_PASSWD_mycontainerreg=$(ACRcontainerreg)
    ACR_PASSWD_anotherregistry=$(ACRreg2)
    ENV_MAIL_PASSWD=$(mailPassword)
  </pre>

Now run the Release-Pipeline or wait for the trigger to kick in. If everything goes well, you should receive a report-mail.
If not, then there might be some misconfiguration or missing access-permissions.
