#include <stdio.h>
#include <inttypes.h>

#include <unistd.h>
#include <termios.h>
#include <fcntl.h>
#include <signal.h>

struct termios terminal_properties = {};

void original_terminal_properties_restore(int sig)
{
  terminal_properties.c_lflag |= ECHO;
  tcsetattr(STDIN_FILENO, TCSANOW, &terminal_properties);
  printf("\nTerminal properties restored. Exiting!\n");
  _exit(0);
}

int main(int argc, char* argv[])
{
  char ch = 0;

  tcgetattr(STDIN_FILENO, &terminal_properties);
  terminal_properties.c_lflag &= ~ECHO;
  tcsetattr(STDIN_FILENO, TCSANOW, &terminal_properties);

  fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK);

  signal(SIGINT, original_terminal_properties_restore);

  while (1)
  {
    ch = getchar();

    if (ch == '\n' || ch == '\r')
    {
      printf("<ENTER> pressed\n");
    }
    else if (ch == EOF)
    {   
      printf("<ENTER> key NOT pressed\n");
    }

    while (getchar() != EOF);
    clearerr(stdin);

    sleep(1);
  }

  return 0;
}
