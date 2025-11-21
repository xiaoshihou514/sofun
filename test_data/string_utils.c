#include <stdio.h>
#include <string.h>

void reverse_string(char* str) {
    if (!str) return;
    
    int len = strlen(str);
    for (int i = 0; i < len / 2; i++) {
        char temp = str[i];
        str[i] = str[len - i - 1];
        str[len - i - 1] = temp;
    }
}

void to_uppercase(char* str) {
    if (!str) return;
    
    while (*str) {
        if (*str >= 'a' && *str <= 'z') {
            *str = *str - 'a' + 'A';
        }
        str++;
    }
}

int string_length(const char* str) {
    if (!str) return 0;
    return strlen(str);
}

int is_palindrome(const char* str) {
    if (!str) return 0;
    
    int len = strlen(str);
    for (int i = 0; i < len / 2; i++) {
        if (str[i] != str[len - i - 1]) {
            return 0;
        }
    }
    return 1;
}
