#include <stdio.h>
#include <inttypes.h>

#include <unistd.h>
#include <termios.h>
#include <fcntl.h>
#include <signal.h>

struct termios terminal_properties = {};

void enter_key_handler(int sig)
{
  char ch = getchar();

  if (ch == '\n' || ch == '\r')
  {
    printf("<ENTER> pressed\n");
  }

  while (getchar() != EOF);
  clearerr(stdin);
}

void original_terminal_properties_restore(int sig)
{
  terminal_properties.c_lflag |= ECHO;
  tcsetattr(STDIN_FILENO, TCSANOW, &terminal_properties);
  printf("\nTerminal properties restored. Exiting!\n");
  _exit(0);
}

int main(int argc, char* argv[])
{
  struct sigaction sa = {};

  sa.sa_handler = enter_key_handler;
  sa.sa_flags = 0;
  sigemptyset(&sa.sa_mask);
  sigaction(SIGIO, &sa, NULL);

  fcntl(STDIN_FILENO, F_SETOWN, getpid());
  fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK | O_ASYNC);

  signal(SIGINT, original_terminal_properties_restore);

  tcgetattr(STDIN_FILENO, &terminal_properties);
  terminal_properties = terminal_properties;
  terminal_properties.c_lflag &= ~ECHO;
  tcsetattr(STDIN_FILENO, TCSANOW, &terminal_properties);

  while (1)
  {
    pause();
  }

  return 0;
}
