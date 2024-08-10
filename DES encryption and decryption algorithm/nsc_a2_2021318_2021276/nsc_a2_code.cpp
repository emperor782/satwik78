#include <iostream>
#include <unordered_map>
#include <vector>
#include <algorithm>
#include <cmath>
#include <bitset>
#include <string>
using namespace std;

// Hexadecimal to binary conversion
string hex2bin(string s){
    unordered_map<char, string> mp = {
        {'0', "0000"}, {'1', "0001"}, {'2', "0010"}, {'3', "0011"},
        {'4', "0100"}, {'5', "0101"}, {'6', "0110"}, {'7', "0111"},
        {'8', "1000"}, {'9', "1001"}, {'A', "1010"}, {'B', "1011"},
        {'C', "1100"}, {'D', "1101"}, {'E', "1110"}, {'F', "1111"}
    };
    string bin = "";
    for (char c : s) {
        bin += mp[c];
    }
    return bin;
}

// Binary to hexadecimal conversion
string bin2hex(string s){
    unordered_map<string, char> mp = {
        {"0000", '0'}, {"0001", '1'}, {"0010", '2'}, {"0011", '3'},
        {"0100", '4'}, {"0101", '5'}, {"0110", '6'}, {"0111", '7'},
        {"1000", '8'}, {"1001", '9'}, {"1010", 'A'}, {"1011", 'B'},
        {"1100", 'C'}, {"1101", 'D'}, {"1110", 'E'}, {"1111", 'F'}
    };
    string hex = "";
    for (int i = 0; i < s.length(); i += 4) {
        string ch = s.substr(i, 4);
        hex += mp[ch];
    }
    return hex;
}

// Binary to decimal conversion
int bin2dec(string binary){
    int decimal = 0, i = 0;
    while (binary != "") {
        int dec = binary.back() - '0';
        decimal += dec * pow(2, i);
        binary.pop_back();
        i++;
    }
    return decimal;
}

// Decimal to binary conversion
string dec2bin(int num){
    bitset<4> binary(num);
    string bin = binary.to_string();
    return bin;
}

// Permute function to rearrange the bits
string permute(string k, vector<int> arr, int n){
    string permutation = "";
    for (int i = 0; i < n; i++) {
        permutation += k[arr[i] - 1];
    }
    return permutation;
}

// Shifting the bits towards left by nth shifts
string shift_left(string k, int nth_shifts){
    for (int i = 0; i < nth_shifts; i++) {
        rotate(k.begin(), k.begin() + 1, k.end());
    }
    return k;
}

// Calculating xor of two strings of binary number a and b
string xor_strings(string a, string b){
    string ans = "";
    for (int i = 0; i < a.length(); i++) {
        if (a[i] == b[i]) {
            ans += "0";
        } 
        else {
            ans += "1";
        }
    }
    return ans;
}

// initial permutation table
vector<int> initial_perm={
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
};

// Expansion P-box Table
vector<int> exp_p={
    32, 1, 2, 3, 4, 5, 4, 5,
    6, 7, 8, 9, 8, 9, 10, 11,
    12, 13, 12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21, 20, 21,
    22, 23, 24, 25, 24, 25, 26, 27,
    28, 29, 28, 29, 30, 31, 32, 1
};

// S-box Table
vector<vector<vector<int>>> sbox={
    {
        {14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7},
        {0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8},
        {4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0},
        {15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13}
    },
    {
        {15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10},
        {3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5},
        {0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15},
        {13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9}
    },
    {   {10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8},
		{13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1},
		{13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7},
		{1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12}
    },
	{   {7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15},
		{13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9},
		{10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4},
		{3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14}
    },
	{   {2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9},
		{14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6},
		{4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14},
		{11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3}
    },
	{   {12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11},
		{10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8},
		{9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6},
		{4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13}
    },
	{   {4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1},
		{13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6},
		{1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2},
		{6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12}
    },
	{   {13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7},
		{1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2},
		{7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8},
		{2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11}
    }
};

// Straight Permutation Table
vector<int> per={
    16, 7, 20, 21, 29, 12, 28, 17,
    1, 15, 23, 26, 5, 18, 31, 10,
    2, 8, 24, 14, 32, 27, 3, 9,
    19, 13, 30, 6, 22, 11, 4, 25
};

// Final Permutation Table
vector<int> final_perm = {
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25
};

vector<string> encrypt(string pt, vector<string>& rkb, string type){
    vector<string> e(3);
    pt = hex2bin(pt);

    // Initial Permutation
    pt = permute(pt, initial_perm, 64);

    string left = pt.substr(0, 32);
    string right = pt.substr(32, 64);
    for (int i = 0; i < 16; i++) {
        // Expansion P-box: Expanding the 32 bits data into 48 bits
        string right_expanded = permute(right, exp_p, 48);

        // XOR RoundKey[i] and right_expanded
        string xor_x = xor_strings(right_expanded, rkb[i]);

        // S-boxes: substituting the value from s-box table by calculating row and column
        string sbox_out = "";
        for (int j = 0; j < 8; j++) {
            string r,c;
            r+= xor_x[j * 6];
            r+= xor_x[j * 6 + 5];
            int row = bin2dec(r);
            c+= xor_x[j * 6 + 1];
            c+= xor_x[j * 6 + 2];
            c+= xor_x[j * 6 + 3];
            c+= xor_x[j * 6 + 4];
            int col = bin2dec( c);
            int val = sbox[j][row][col];
            sbox_out += dec2bin(val);
        }
        // Straight P-box: After substituting rearranging the bits
        string sp_box = permute(sbox_out, per, 32);

        // XOR left and sp_box
        string result = xor_strings(left, sp_box);  
        left = result;

        string s = left; //swap
        left= right;
        right = s;
        
        if(i==0||i==1||i==13||i==14){
            if((i==0||i==13)&&(type=="e")){ //encrypt round values
                if(i==0){
                    string s = bin2hex(left)+" "+bin2hex(right);
                    e[1] =s;
                }
                else if(i==13){
                    string t = bin2hex(left)+" "+bin2hex(right);
                    e[2] =t;
                }
            }
            else if((i==1||i==14)&&(type=="d")){  //dencrypt round values
                if(i==14){
                    string u = bin2hex(right)+" "+bin2hex(left);
                    e[1] =u;
                }
                else if(i==1){
                    string v = bin2hex(right)+" "+bin2hex(left);
                    e[2] =v;
                }
            }
        }
        //cout<<"Round "<< i + 1<<": "<<bin2hex(left)<<" "<<bin2hex(right)<<endl;
    }
    string s = left;
    left= right;
    right = s;
    
    string combine = left + right;

    // Final permutation: final rearranging of bits to get cipher text
    string cipher_text = permute(combine, final_perm, 64);
    e[0]= bin2hex(cipher_text);
    return e;
}

void des(vector<string>& pt, vector<string>& ck){
    for(int i=0;i<3;i++){
        string key = hex2bin(ck[i]);
    
        // --parity bit drop table
        vector<int> keyp = {
            57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18,
            10, 2, 59, 51, 43, 35, 27, 19, 11, 3, 60, 52, 44, 36,
            63, 55, 47, 39, 31, 23, 15, 7, 62, 54, 46, 38, 30, 22,
            14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 28, 20, 12, 4
        };

        // getting 56 bit key from 64 bit using the parity bits
        key = permute(key, keyp, 56);
    
        // Number of bit shifts
        vector<int> shift_table = {1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1};
    
        // Key- Compression Table : Compression of key from 56 bits to 48 bits
        vector<int> key_comp = {
            14, 17, 11, 24, 1, 5, 3, 28, 15, 6, 21, 10, 23, 19, 12, 4,
            26, 8, 16, 7, 27, 20, 13, 2, 41, 52, 31, 37, 47, 55, 30, 40,
            51, 45, 33, 48, 44, 49, 39, 56, 34, 53, 46, 42, 50, 36, 29, 32
        };
    
        // Splitting
        string left = key.substr(0, 28); 
        string right = key.substr(28, 56); 
    
        vector<string> rkb; // rkb for RoundKeys in binary
        for (int i = 0; i < 16; i++) {
            // Shifting the bits by nth shifts by checking from shift table
            left = shift_left(left, shift_table[i]);
            right = shift_left(right, shift_table[i]);
    
            string combine_str = left + right;
    
            // Compression of key from 56 to 48 bits
            string round_key = permute(combine_str, key_comp, 48);
    
            rkb.push_back(round_key);
            
        }
    
        vector<string> ct(3);
        ct = encrypt(pt[i], rkb, "e"); //encryption
        
        reverse(rkb.begin(), rkb.end());
       
        
        vector<string> text(3);
        text = encrypt(ct[0], rkb, "d");  //decryption
        
        cout<<"pair - "<<i+1<<endl;
        for(int j=0;j<3;j++){
            if(j==0){
                if(text[j] == pt[i]){
                    cout<<"matched "<<"ciphertext: "<<ct[j]<<" generated plaintext: "<<text[j]<<endl;
                }
                else{
                    cout<<"generated plaintext not matched"<<endl;
                }
            }
            else if(j==1){
                if(text[j] == ct[j]){
                    cout<<"matched "<<"1st encrytption: "<<ct[j]<<"- 15th decryption: "<<text[j]<<endl;
                }
                else{
                    cout<<"generated texts not matched"<<endl;
                }
            }
            else if(j==2){
                if(text[j] == ct[j]){
                    cout<<"matched "<<"14th encrytption: "<<ct[j]<<" 2nd decryption: "<<text[j]<<endl;
                }
                else{
                    cout<<"generated texts not matched"<<endl;
                }
            }
        }
    }
}

int main(){
    
    vector<string> pt(3);
    vector<string> ck(3);
    // for (int i = 0; i < 3; i++) {
    //     cout << "Enter plaintext " << i + 1 << " (16 hexadecimal characters): ";
    //     cin >> pt[i];
        
    //     cout << "Enter cipher key " << i + 1 << " (16 hexadecimal characters): ";
    //     cin >> ck[i];
    //     if (pt[i].length() != 16 || ck[i].length() != 16) {
    //         cout << "Please enter 16 hexadecimal characters." << endl;
    //         return 0;
    //     }
    // }
    pt[0] = "02468ACEECA86420";
    ck[0] = "0F1571C947D9E859";
    pt[1] = "23D58A1002FBC891";
    ck[1] = "4B72A09DE0A1BFC3";
    pt[2] = "5CDF9000358A0B27";
    ck[2] = "2EA11460DBF77269";
    des(pt,ck);

    return 0;
}
