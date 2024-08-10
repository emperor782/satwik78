#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

#include <cmath>
#include <sstream>
using namespace std;

string hash_fun(const string& input) {
    string hashString;

    // Perform some simple hash operation, e.g., sum of ASCII values
    int hashValue = 0;
    for (char ch : input) {
        hashValue += static_cast<int>(ch);
    }

    // Generate the hash string with lowercase alphabets
    for (int i = 0; i < 8; ++i) {
        char hashChar = 'a' + (hashValue % 26);
        hashString += hashChar;
        hashValue = (hashValue * 37) % 101;  // Some arbitrary hashing operation
    }

    return hashString;
}

string join(const string& a, const string& b){
    return a+b;
}


// Function to perform transposition encryption
string encrypt(string str, string key) {
    int keyLength = key.size();
    int strLength = str.size();
    int numRows = (strLength / keyLength) + (strLength % keyLength ? 1 : 0);
    //cout<<numCols;
    // Create a matrix to store the characters
    char matrix[numRows][keyLength];

    // Populate the matrix with the characters from the string
    int index = 0;
    for (int row = 0; row < numRows; row++) {
        for (int col = 0; col < keyLength; col++) {
            if (index < strLength) {
                matrix[row][col] = str[index++];
            } else {
                matrix[row][col] = '-';  // Padding with '-' if necessary
            }
        }
    }

    // Build the encrypted string by reading the matrix row-wise based on the key
    string result="";
    for (int i = 0; i < numRows*keyLength; i++) {
        result+='0';
    }
    //cout<<result<<endl;
    int j =0;
    for (char ch : key) {
        int col = int(ch) - int('0');
        int x = (col-1)*numRows;
        for (int row = 0; row < numRows; row++) {
            result[x] = matrix[row][j];
            x++;
        }
        j++;
    }
    return result;
}

string decrypt(string str, string key) {
    int keyLength = key.size();
    int strLength = str.size();
    int numRows = (strLength / keyLength) + (strLength % keyLength ? 1 : 0);

    
    char matrix[numRows][keyLength];

    
    int j = 0;
    for (char ch : key) {
        int col = int(ch) - int('0');
        int x = (col-1)*numRows;
        for (int row = 0; row < numRows; row++) {
            matrix[row][j] = str[x];
            x++;
            
        }
        j++;
    }
    // Build the decrypted string by reading the matrix row-wise
    string result = "";
    for (int row = 0; row < numRows; row++) {
        for (int col = 0; col < keyLength; col++) {
            if (matrix[row][col] != '-') {  // Skip padding '-' characters
                result += matrix[row][col];
            }
        }
    }
    return result;
}


bool is_recognizable(const string& plaintext) {
    // Check if all characters are lowercase
    for (char ch : plaintext) {
        if (!(ch >= 'a' && ch <= 'z')) {
            return false;  
        }
    }

    return true;
}




void generateStringsHelper(int l, std::vector<int>& digits, std::vector<int>& current, std::vector<std::string>& result, const string ciphertext[], int& flag) {
    if (current.size() == l) {
        std::string str;
        for (int digit : current) {
            str += std::to_string(digit);
        }
        //result.push_back(str);
        int count = 0;
            
            string key = str;
            for(int k=0;k<5;k++){
             // Decrypt the ciphertext using the current key
                string decryptedText = decrypt(ciphertext[k], key);
                
                int n= decryptedText.length();
                
                if ( n >= 8) {
                    string orig_text = decryptedText.substr(0,n-8);
                    string hash_val = decryptedText.substr(n-8, n);
                    string hash_str = hash_fun(orig_text);
                    
                    if (hash_val == hash_str) {
                        count++;
                    } 
                    else {
                        break; // Restart
                    }
                } 
                else{
                    break;
                }
            }
            if(count==5){
                flag=1;
                cout<<"key found = "<<key<<endl;
                exit;
            }
        return;
    }

    for (int digit : digits) {
        if (std::find(current.begin(), current.end(), digit) == current.end()) {
            current.push_back(digit);
            generateStringsHelper(l, digits, current, result, ciphertext,flag);
            current.pop_back();
        }
    }
}

std::vector<std::string> generateStrings(int l, const string ciphertext[], int& flag) {
    std::vector<int> digits;
    for (int i = 1; i <= l; ++i) {
        digits.push_back(i);
    }

    std::vector<std::string> result;
    std::vector<int> current;
    generateStringsHelper(l, digits, current, result, ciphertext, flag);

    return result;
}
// Function to perform brute-force attack and find a key that satisfies π
int bruteForceAttack(const string ciphertext[]) {
    string plainText;
    int flag=0;
    // Loop through all possible keys
    for (int i = 1; i < 10; i++) {
        vector<int> current;
        vector<bool> used(i + 1, false);
        
        generateStrings(i, ciphertext,flag);
    }
    if(flag==0)
    cout<<"key not found"<<endl;
    return 0;
}

int main() {
    
    string originaltext[5], key;
    for(int i=0;i<5;i++){
        string s;
        cin>>s;
        originaltext[i] = s;
    }
    cin>> key;
    string ciphertext[5],hash_str[5];
    
    for(int i=0;i<5;i++){
        hash_str[i] = hash_fun(originaltext[i]);
        string plaintext = join(originaltext[i],hash_str[i]);
        
        if(is_recognizable(plaintext)){
            ciphertext[i] = encrypt(plaintext,key);
            
        }
        else{
            cout<<"plaintext not recognizable"<<endl;
            exit;
        }
    }
    
    bruteForceAttack(ciphertext);
    return 0;
}

