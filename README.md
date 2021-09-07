# Setting up the application

This folder contains backend of the spring boot web application which automatically includes built frontend code in the target folder.

The jar file can be found in the target folder also which allows the application to be deployed to an AWS server.

The recommender feature needs to be deployed seperately it can be found in the folder python_application_TFIDF and then the url changed in generateRecommendationList() in Controller/PositionController.

The database details need to be entered in resources/application.properties once the database has been created the if the application is built with ```mvn clean install``` then the tables will be automatically created. After the tables have been created two roles need to be added into the ```roles``` table -> ```ROLE_STUDENT``` and ```ROLE_LECTURER```. N.B. If these are not entered the application will not work!

If the frontend code needs to be changed it can be found in the allocastion-system-frontend folder. The command ```npm install``` needs to be ran from the project folder to install the node modules.
