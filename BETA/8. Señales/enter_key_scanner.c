#include <stdio.h>

#include <unistd.h>
#include <termios.h>
#include <fcntl.h>

int main(int argc, char* argv[])
{
  struct termios terminal_properties = {};
  char           ch                  = 0;

  tcgetattr(STDIN_FILENO, &terminal_properties);
  terminal_properties.c_lflag &= ~ECHO;
  tcsetattr(STDIN_FILENO, TCSANOW, &terminal_properties);

  fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK);

  while (1)
  {
    ch = getchar();

    if (ch == '\n' || ch == '\r')
    {
      printf("<ENTER> pressed\n");
    }
    else
    {   
      printf("<ENTER> key NOT pressed\n");
    }

    while (getchar() != EOF);
    clearerr(stdin);

    sleep(1);
  }

  return 0;
}
