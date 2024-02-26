import 'package:flutter/material.dart'; // Importing the material package which contains widgets for creating UIs in Flutter

class RandomWidget extends StatelessWidget { // Defining a stateless widget named RandomWidget
  @override
  Widget build(BuildContext context) { // Override the build method to describe the UI
    return Scaffold( // Scaffold widget provides a framework to implement the basic material design layout of the application
      appBar: AppBar( // AppBar widget represents the app bar at the top of the Scaffold
        title: Text('Random Widget'), // Text widget for displaying the title of the app bar
      ),
      body: Center( // Center widget aligns its child in the center of the screen
        child: Column( // Column widget arranges its children in a vertical array
          mainAxisAlignment: MainAxisAlignment.center, // Aligning the children vertically centered
          children: <Widget>[ // List of children widgets
            Text( // Text widget to display some text
              'This is a random widget.', // Text content
              style: TextStyle(fontSize: 20), // Text style with font size 20
            ),
            SizedBox(height: 20), // SizedBox widget for adding spacing between widgets
            ElevatedButton( // ElevatedButton widget for creating a button
              onPressed: () {
                // Do something when the button is pressed. For example, you could navigate to another screen, update some state, or perform any other action.
              },
              child: Text('Press Me'), // Text displayed on the button
            ),
          ],
        ),
      ),
    );
  }
}

void main() {
  runApp(MaterialApp( // runApp function to start the app with the given widget. MaterialApp is a widget that provides several utility widgets commonly needed by applications implementing Material Design, such as a Navigator, Theme, and more.
    home: RandomWidget(), // Setting RandomWidget as the home page of the app
  ));
}
