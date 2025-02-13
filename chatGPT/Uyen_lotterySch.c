#include "types.h"
#include "param.h"
#include "memlayout.h"
#include "riscv.h"
#include "spinlock.h"
#include "proc.h"
#include "defs.h"

struct cpu cpus[NCPU];

struct proc proc[NPROC];

struct proc *initproc;

int nextpid = 1;
struct spinlock pid_lock;

extern void forkret(void);
static void freeproc(struct proc *p);

extern char trampoline[]; // trampoline.S

// helps ensure that wakeups of wait()ing
// parents are not lost. helps obey the
// memory model when using p->parent.
// must be acquired before any p->lock.
struct spinlock wait_lock;

///...... some code here

// lottery scheduler
// we need to access function srand() from sysproc.c
extern int sys_srand(void);

// helper struct to keep track of range for each proc
struct range_proc
{
    int range_start;   // Start of the ticket range
    int range_end;     // End of the ticket range
    struct proc *proc; // Pointer to the process
};

// Function: scheduler
// --------------------
// Implements a lottery scheduler where processes are assigned tickets,
// and a winner is chosen randomly. Processes with more tickets have
// higher chances of winning the lottery.
void scheduler(void)
{
    struct proc *p;
    struct cpu *c = mycpu();
    int total_tickets = 0;
    int ticket_ranges[NPROC][2];          // Array to store ticket ranges for each process
    struct range_proc range_procs[NPROC]; // Array to store processes with their ticket ranges
    int i;
    int rand_num = 0;            // Random number generated for lottery
    struct proc *winnerProc = 0; // Pointer to the winning process

    c->proc = 0;
    sys_srand(); // Seed the random number generator

    for (;;)
    {
        // Avoid deadlock by ensuring that devices can interrupt.
        intr_on();

        // Calculate total tickets and assign ticket ranges
        total_tickets = 0;
        for (i = 0, p = proc; p < &proc[NPROC]; i++, p++)
        {
            if (p->state != UNUSED)
            {
                // Assign ticket range for each process
                // Ticket range is determined by the cumulative sum of tickets
                // Example:
                //  Process A with 10 tickets, Process B with 20 tickets
                //  Process A: ticket range [0, 9], Process B: ticket range [10, 29]
                ticket_ranges[i][0] = total_tickets;
                ticket_ranges[i][1] = total_tickets + p->tickets - 1;
                total_tickets += p->tickets;

                // Store process pointer with its ticket range
                range_procs[i].range_start = ticket_ranges[i][0];
                range_procs[i].range_end = ticket_ranges[i][1];
                range_procs[i].proc = p;
            }
        }

        // If no runnable processes, skip
        if (total_tickets != 0)
        {
            // Pick a random number within the range of total tickets
            rand_num = sys_srand() % total_tickets;

            // Find the winner
            for (i = 0; i < NPROC; i++)
            {
                // Skip processes that are not runnable
                if (range_procs[i].proc == 0 || range_procs[i].proc->state != RUNNABLE)
                    continue;

                // Check if the random number falls within the range of this process
                if (rand_num >= range_procs[i].range_start && rand_num <= range_procs[i].range_end)
                {
                    winnerProc = range_procs[i].proc;
                    break;
                }
            }
        }

        // If no winner, skip, otherwise switch to winner
        if (winnerProc != 0)
        {
            // Switch to chosen process
            acquire(&winnerProc->lock);
            if (winnerProc->state == RUNNABLE)
            {
                // Update ticket ranges if process completed
                for (i = 0; i < NPROC; i++)
                {
                    if (proc[i].state != UNUSED)
                    {
                        // Adjust ticket ranges based on the winner's range
                        // -------------------------------------------------
                        // This section adjusts the ticket ranges of other processes based on the winning process's range.
                        // The adjustments ensure that the winning process's tickets are properly accounted for and that
                        // ticket ranges remain valid for all processes.

                        // Case 1: Winner's range falls completely below the current process's range
                        // ----------------------------------------------------------------------
                        // If the start of the winner's range is greater than the end of the current process's range,
                        // it means that the winner's range is completely below the current process's range.
                        // In this case, both the start and end of the current process's range are decreased by the
                        // number of tickets held by the winning process, effectively shifting the range upward.
                        if (ticket_ranges[i][0] > ticket_ranges[winnerProc->pid][1])
                        {
                            ticket_ranges[i][0] -= winnerProc->tickets;
                            ticket_ranges[i][1] -= winnerProc->tickets;
                        }

                        // Case 2: Winner's range falls completely above the current process's range
                        // -----------------------------------------------------------------------
                        // If the end of the winner's range is less than the start of the current process's range,
                        // it means that the winner's range is completely above the current process's range.
                        // In this case, no adjustment is needed as the winner's range does not affect the current process's range.

                        // Case 3: Winner's range completely encompasses the current process's range
                        // -----------------------------------------------------------------------
                        // If the start of the winner's range is greater than or equal to the start of the current process's range,
                        // and the end of the winner's range is less than or equal to the end of the current process's range,
                        // it means that the winner's range completely encompasses the current process's range.
                        // In this case, the current process's range is invalidated by setting both the start and end to -1.
                        else if (ticket_ranges[i][0] >= ticket_ranges[winnerProc->pid][0] && ticket_ranges[i][1] <= ticket_ranges[winnerProc->pid][1])
                        {
                            ticket_ranges[i][0] = -1;
                            ticket_ranges[i][1] = -1;
                        }

                        // Case 4: Winner's range partially overlaps with the current process's range (below)
                        // -------------------------------------------------------------------------------
                        // If the start of the winner's range is less than the start of the current process's range,
                        // and the end of the winner's range is greater than the end of the current process's range,
                        // it means that the winner's range partially overlaps with the lower part of the current process's range.
                        // In this case, only the end of the current process's range is adjusted downwards by the
                        // number of tickets held by the winning process, effectively shortening the range.
                        else if (ticket_ranges[i][0] < ticket_ranges[winnerProc->pid][0] && ticket_ranges[i][1] > ticket_ranges[winnerProc->pid][1])
                        {
                            ticket_ranges[i][1] -= winnerProc->tickets;
                        }

                        // Case 5: Winner's range partially overlaps with the current process's range (above)
                        // -------------------------------------------------------------------------------
                        // If the start of the winner's range is greater than the start of the current process's range,
                        // and the end of the winner's range is less than the end of the current process's range,
                        // it means that the winner's range partially overlaps with the upper part of the current process's range.
                        // In this case, only the end of the current process's range is adjusted upwards to one less than
                        // the start of the winner's range, effectively truncating the range.
                        else if (ticket_ranges[i][0] < ticket_ranges[winnerProc->pid][0])
                        {
                            ticket_ranges[i][1] = ticket_ranges[winnerProc->pid][0] - 1;
                        }

                        // Case 6: Winner's range partially overlaps with the current process's range (below)
                        // -------------------------------------------------------------------------------
                        // If the end of the winner's range is greater than the end of the current process's range,
                        // and the start of the winner's range is less than the start of the current process's range,
                        // it means that the winner's range partially overlaps with the lower part of the current process's range.
                        // In this case, only the start of the current process's range is adjusted upwards to one more than
                        // the end of the winner's range, effectively truncating the range.
                        else if (ticket_ranges[i][1] > ticket_ranges[winnerProc->pid][1])
                        {
                            ticket_ranges[i][0] = ticket_ranges[winnerProc->pid][1] + 1;
                        }

                        // Default Case: Unexpected scenario
                        // ----------------------------------
                        // This case handles unexpected scenarios where the winner's range overlaps with the current process's range
                        // in a way not covered by the previous cases. In such cases, the current process's range is invalidated by
                        // setting both the start and end to -1.
                        else
                        {
                            ticket_ranges[i][0] = -1;
                            ticket_ranges[i][1] = -1;
                        }
                    }
                }

                // Switch to chosen process
                winnerProc->state = RUNNING;
                c->proc = winnerProc;
                swtch(&c->context, &winnerProc->context);
                c->proc = 0;
            }
            release(&winnerProc->lock);
        }
    }
}

///...... some code here

// refactoring code with detail comments
// Define a structure to represent the range of tickets for each process
struct TicketRange
{
    int start; // Start of the ticket range
    int end;   // End of the ticket range
};

// Function: calculateTotalTickets
// -------------------------------
// Calculates the total number of tickets among all runnable processes.
// Parameters:
//    - procs: Pointer to an array of processes
//    - num_procs: Number of processes in the array
// Returns:
//    - The total number of tickets among all runnable processes.
int calculateTotalTickets(struct proc *procs, int num_procs)
{
    int total_tickets = 0;
    for (int i = 0; i < num_procs; i++)
    {
        if (procs[i].state != UNUSED)
        {
            total_tickets += procs[i].tickets;
        }
    }
    return total_tickets;
}

// Function: pickWinner
// ---------------------
// Picks the winning process based on a random number and the ticket ranges of processes.
// Parameters:
//    - procs: Pointer to an array of processes
//    - ranges: Pointer to an array of TicketRange structures representing the ticket ranges of processes
//    - num_procs: Number of processes in the array
//    - total_tickets: Total number of tickets among all runnable processes
//    - rand_num: Random number used to pick the winner
// Returns:
//    - Pointer to the winning process if found, otherwise returns 0.
struct proc *pickWinner(struct proc *procs, struct TicketRange *ranges, int num_procs, int total_tickets, int rand_num)
{
    for (int i = 0; i < num_procs; i++)
    {
        if (procs[i].state == RUNNABLE && rand_num >= ranges[i].start && rand_num <= ranges[i].end)
        {
            return &procs[i];
        }
    }
    return 0; // No winner found
}

// Function: scheduler
// --------------------
// Implements a lottery scheduler where processes are assigned tickets,
// and a winner is chosen randomly. Processes with more tickets have
// higher chances of winning the lottery.
// This function continuously runs, selecting a winner based on the number of tickets
// each process holds. The winner is then scheduled to run by switching the CPU context
// to the winner's process context.
void scheduler(void)
{
    struct proc *p;              // Pointer to a process
    struct cpu *c = mycpu();     // Pointer to the current CPU
    struct proc *winnerProc = 0; // Pointer to the winning process
    int rand_num = 0;            // Random number generated for lottery

    c->proc = 0; // Clear the current process from the CPU
    sys_srand(); // Seed the random number generator

    for (;;)
    {              // Infinite loop for continuous scheduling
        intr_on(); // Enable interrupts

        // Calculate total tickets and assign ticket ranges
        int total_tickets = calculateTotalTickets(proc, NPROC); // Total number of tickets among all processes
        struct TicketRange ranges[NPROC];                       // Array to store ticket ranges for each process
        int current_ticket = 0;                                 // Counter for current ticket allocation
        for (int i = 0; i < NPROC; i++)
        {
            if (proc[i].state != UNUSED)
            {
                // Assign ticket range for each process
                ranges[i].start = current_ticket;
                ranges[i].end = current_ticket + proc[i].tickets - 1;
                current_ticket = ranges[i].end + 1;
            }
        }

        // If there are runnable processes with tickets, proceed with lottery selection
        if (total_tickets != 0)
        {
            rand_num = sys_srand() % total_tickets;                                // Generate a random number within the range of total tickets
            winnerProc = pickWinner(proc, ranges, NPROC, total_tickets, rand_num); // Select the winner process
        }

        // If a winner is found, acquire its lock and switch to its context to execute
        if (winnerProc != 0)
        {
            acquire(&winnerProc->lock); // Acquire lock to prevent race conditions
            if (winnerProc->state == RUNNABLE)
            {
                // Set the state of the winner process to RUNNING
                winnerProc->state = RUNNING;
                // Switch the CPU context to the winner process context
                c->proc = winnerProc;
                swtch(&c->context, &winnerProc->context); // Perform context switch
                c->proc = 0;                              // Clear the CPU process after context switch
            }
            release(&winnerProc->lock); // Release the lock after executing the winner process
        }
    }
}
