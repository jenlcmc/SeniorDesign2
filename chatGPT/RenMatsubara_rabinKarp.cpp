#include <cstring>
#include <iostream>
using namespace std;

const int d = 256;  // The number of characters in the input alphabet

// Function to perform the Rabin-Karp pattern matching algorithm
void rabinKarp(char pattern[], char text[], int q) {
    int m = strlen(pattern);  // Length of the pattern
    int n = strlen(text);     // Length of the text
    int i, j;
    int p = 0;  // Hash value for pattern
    int t = 0;  // Hash value for text
    int h = 1;

    // Calculate (d^(m-1)) % q
    for (i = 0; i < m - 1; i++)
        h = (h * d) % q;

    // Calculate initial hash values for pattern and text
    for (i = 0; i < m; i++) {
        p = (d * p + pattern[i]) % q;
        t = (d * t + text[i]) % q;
    }

    // Iterate through the text with a sliding window to find matches
    for (i = 0; i <= n - m; i++) {
        // Check if hash values match, then check character by character
        if (p == t) {
            for (j = 0; j < m; j++) {
                if (text[i + j] != pattern[j])
                    break;
            }

            // If the inner loop completed, a match is found
            if (j == m)
                cout << "Pattern is found at position: " << i + 1 << endl;
        }

        // Update the hash value for the next window in the text
        if (i < n - m) {
            t = (d * (t - text[i] * h) + text[i + m]) % q;

            // Ensure the hash value is non-negative
            if (t < 0)
                t = (t + q);
        }
    }
}


int main() {

   // char text[] = "ABCCDXAEFGX";
    char text[] = "QWERTYUIOPASDFGHJKLXQWERTYUIOPASDFGHJKLX";
    char pattern[] = "KLXQW";
    int q = 13;
    rabinKarp(pattern, text, q);
} 