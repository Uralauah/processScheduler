import threading
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import random

class GanttChart:
    def __init__(self, master):
        self.canvas = tk.Canvas(master, height=100, bg='white') #간트차트가 그려질 캔버스 생성
        self.canvas.pack(fill='both', expand=True)
        self.processes = {}
        self.last_end_time = 0
        

    #프로세스 추가
    def add_process(self, name, start_time, duration, priority, color):
        start_time = max(self.last_end_time, start_time)
        y_position = 1 * 40 + 20
        for i in range(duration):
            self.canvas.after(i * 1000, self.draw_process, name, start_time + i, 1, y_position, priority, color)
        self.last_end_time = start_time + duration
        

    #간트차트 그리기 
    def draw_process(self, name, start_time, duration, y, priority, color):
        x0 = start_time * 20 + 10
        x1 = (start_time + duration) * 20 + 10
        self.canvas.create_rectangle(x0, y, x1, y + 30, fill=color, outline="black")
        self.canvas.create_text(x0 + 5, y + 15, text=f"{name}", anchor="w", fill="black")

    #리셋
    def clear(self):
        self.canvas.delete("all")
        self.processes = {}
        self.last_end_time = 0
        

process_data = []

root = tk.Tk()
root.title("Processor Scheduling Simulation")
gantt_chart = GanttChart(root)
scheduling_type = tk.StringVar(value="FIFO")

timer_var = tk.StringVar(value="Time elapsed: 0s")

def add_process():
    processor_name = processor_name_var.get()
    burst_time = burst_time_var.get()
    arrive_time = arrive_time_var.get()
    priority = priority_var.get()
    deadline = 0
    time_quantum=0
    if scheduling_type.get() == "Deadline based aging":
        deadline = deadline_var.get()

    if scheduling_type.get() == "Priority based Round-Robin":
        time_quantum = 1+int(priority)//10

    # 하나라도 입력되지 않았을 경우 경고
    if not (processor_name and burst_time and arrive_time and priority):
        messagebox.showwarning("Warning", "모든 필드를 입력해야 합니다.")
        return
    if scheduling_type.get() == "Deadline based aging":
        if not deadline:
            messagebox.showwarning("Warning", "해당 알고리즘은 deadline을 입력해야 합니다.")
            return

    color = determine_color(len(process_data) + 1)
    info = { #프로세스 정보 저장
        'name': processor_name,
        'burst_time': int(burst_time),
        'arrive_time': int(arrive_time),
        'priority': int(priority),
        'color': color,
        'deadline' :int(deadline),
        'time_quantum' : int(time_quantum),
    }
    process_data.append(info)
    processor_name_entry.delete(0, tk.END)
    burst_time_entry.delete(0, tk.END)
    arrive_time_entry.delete(0, tk.END)
    priority_entry.delete(0, tk.END)
    deadline_entry.delete(0,tk.END)
    #프로세스 정보 listbox로 GUI에 출력
    if scheduling_type.get() == "Deadline based aging":
        process_listbox.insert(tk.END, f"{info['name']} - Burst Time: {info['burst_time']}, Arrive: {info['arrive_time']}, Priority: {info['priority']}, Color: {info['color']}, Deadline: {info['deadline']}")
    else:
        process_listbox.insert(tk.END, f"{info['name']} - Burst Time: {info['burst_time']}, Arrive: {info['arrive_time']}, Priority: {info['priority']}, Color: {info['color']}")

# 색상 지정 함수
def determine_color(process_number):
    colors = ["red", "orange", "yellow", "green", "blue"]
    return colors[(process_number - 1) % len(colors)]

#프로세스 실행
def run_process(process, start_event, end_event, start_time, duration):
    start_event.set() #시작 이벤트를 활성화해서 프로세스 시작 신호를 보냄
    end_event.clear() #종료 이벤트 초기화하여 이전의 종료 신호 지움

    name = process['name']
    priority = process['priority']
    color = process['color']

    #간트차트에 프로세스 그리기
    gantt_chart.add_process(name, start_time, duration, priority, color)
    time.sleep(duration) #프로세스 실행 시간만큼 대기

    end_event.set() #프로세스 끝났음을 알리기 위해 종료 이벤트 설정
    start_event.clear() #다음 프로세스의 시작을 위해 시작 이벤트 초기화

#타이머 업데이트
def update_timer():
    global process_data #프로세스 데이터 저장을 위한 전역 변수
    global start_time #전체 프로세스가 시작된 시간 저장을 위한 전역 변수
    while process_data:  # 프로세스 데이터가 존재하는 동안 반복
        elapsed_time = int(time.time() - start_time)  #시작부터 현재까지 시간 경과 계산
        timer_var.set(f"Time elapsed: {elapsed_time} s") #계산된 결과 타이머 변수에 설정
        time.sleep(1)  #1초 대기
    final_time = int(time.time() - start_time)  #모든 프로세스가 끝난 후 시간 계산
    timer_var.set(f"Total Time: {final_time} s") #최종 시간 타이머 변수에 설정

#Round-Robin을 선택했을 때 time_quantum 입력을 위한 입력창 보이게 하기
def scheduling_type_changed(event=None):
    if scheduling_type.get() == "Round-Robin" or scheduling_type.get() ==  "Round-Robin with aging": 
        time_quantum_label.pack(fill='x', padx=10)
        time_quantum_entry.pack(fill='x', padx=10, pady=2)
        deadline_label.pack_forget()  # 데드라인 입력창 숨김
        deadline_entry.pack_forget()  # 데드라인 입력창 숨김
    elif scheduling_type.get() == "Deadline based aging":
        time_quantum_label.pack_forget()  # time_quantum 입력창 숨김
        time_quantum_entry.pack_forget()  # time_quantum 입력창 숨김
        deadline_label.pack(fill='x', padx=10)  # 데드라인 입력창 표시
        deadline_entry.pack(fill='x', padx=10, pady=2)  # 데드라인 입력창 표시
    else: #선택된 알고리즘이 Round-Robin이 아니라면 입력창 숨기기
        time_quantum_label.pack_forget()
        time_quantum_entry.pack_forget()
        deadline_label.pack_forget()  # 데드라인 입력창 숨김
        deadline_entry.pack_forget()  # 데드라인 입력창 숨김

#시뮬레이션 시작
def start_simulation():
    global start_time 
    start_event = threading.Event()
    end_event = threading.Event()
    start_time = time.time() #시작 시간 초기화
    #스케줄링 유형에 따라 실행
    scheduling = scheduling_type.get()
    time_quantum = None
    if scheduling == "Round-Robin" or scheduling == "Round-Robin with aging": #Round-Robin이면 time_quantum 값 가져오기
        time_quantum = int(time_quantum_var.get())
    #프로세스 스케줄링 시작을 위한 스레드 시작
    threading.Thread(target=simulate_processes, args=(start_event, end_event,scheduling_type.get(),time_quantum)).start()
    #타이머 업데이트 스레드 시작
    threading.Thread(target=update_timer).start() 
    refresh_ui()

def update_process_listbox():
    process_listbox.delete(0, tk.END)  # 기존 목록을 삭제
    for process in process_data:
        # Listbox에 프로세스 정보와 현재 우선순위를 포함하여 추가
        if scheduling_type.get() == "Deadline based aging":
            process_listbox.insert(tk.END, f"{process['name']} - Burst Time: {process['burst_time']}, Arrive: {process['arrive_time']}, Priority: {process['priority']:.2f}, Color: {process['color']}, Deadline: {process['deadline']}")
        elif scheduling_type.get() =="Priority based Round-Robin":
            process_listbox.insert(tk.END, f"{process['name']} - Burst Time: {process['burst_time']}, Arrive: {process['arrive_time']}, Priority: {process['priority']:.2f}, Color: {process['color']}, Time-Quantum: {process['time_quantum']}")
        else:
            process_listbox.insert(tk.END, f"{process['name']} - Burst Time: {process['burst_time']}, Arrive: {process['arrive_time']}, Priority: {process['priority']:.2f}, Color: {process['color']}")

def refresh_ui():
    """ UI 업데이트를 주기적으로 호출하는 함수 """
    if process_data:
        update_process_listbox()  # 프로세스 목록 업데이트
        root.after(1000, refresh_ui)  # 1초 후 다시 호출

#최종 결과 계산
def calculate_metrics(processes):
    total_waiting_time = 0
    total_turnaround_time = 0
    total_response_time = 0  # 응답 시간 총합을 저장할 변수

    #GUI에 실행 후 상세 정보 출력
    process_listbox.insert(tk.END, "Process Execution Details:")
    for process in processes:
        #각 프로세스의 시작시간, 종료시간 계산
        start_time = min(process['start_times'])
        end_time = max(process['end_times'])
        #각 프로세스의 turnaround time, waiting time, response time 계산
        turnaround_time = end_time - process['arrive_time']
        waiting_time = turnaround_time - sum(process['execution_times'])
        response_time = process['first_response_time'] - process['arrive_time']

        #모든 프로세스의 waiting time, turnaround time, response time 더하기
        total_waiting_time += waiting_time
        total_turnaround_time += turnaround_time
        total_response_time += response_time  # 응답 시간 더하기

        #프로세스 별 상세 정보 출력
        process_details = f"Process {process['name']}: Turnaround Time = {turnaround_time}, Waiting Time = {waiting_time}, Response Time = {response_time}"
        process_listbox.insert(tk.END, process_details)

    #average waiting time, average turnaround time, average response time 계산 후 출력
    average_waiting_time = total_waiting_time / len(processes)
    average_turnaround_time = total_turnaround_time / len(processes)
    average_response_time = total_response_time / len(processes)  # 평균 응답 시간 계산
    process_listbox.insert(tk.END, f"Average Waiting Time: {average_waiting_time:.2f}")
    process_listbox.insert(tk.END, f"Average Turnaround Time: {average_turnaround_time:.2f}")
    process_listbox.insert(tk.END, f"Average Response Time: {average_response_time:.2f}")  # 평균 응답 시간 출력
    
def simulate_processes(start_event, end_event, scheduling_type, time_quantum=None):
    global process_data
    current_time = 0
    process_queue = []
    arrival_index=0

    for process in process_data:
        process['start_times'] = []
        process['end_times'] = []
        process['execution_times'] = []
        process['first_response_time'] = None

    def run_idle_process(start_time, duration):
        color = 'white'
        info = {
            'name': ' ',
            'burst_time': duration,
            'arrive_time': start_time,
            'priority': 0,
            'color': color
        }
        run_process(info, start_event, end_event, start_time, duration)
        
    #First Come First In
    if scheduling_type == "FCFS":
        process_data.sort(key=lambda x: x['arrive_time'])
        last_end_time = 0
        for process in process_data:
            #다음에 들어올 프로세스의 도착시간과 마지막으로 종료한 프로세스의 종료시간 사이에 idle한 시간이 존재한다면 빈 간트차트 출력
            if process['arrive_time']>last_end_time:
                run_idle_process(last_end_time,process['arrive_time']-last_end_time)

            start_time = max(last_end_time, process['arrive_time']) #시작 시간 설정
            process['start_times'].append(start_time)
            process['execution_times'].append(process['burst_time'])
            process['end_times'].append(start_time + process['burst_time'])
            if process['first_response_time']==None: #response time 설정
                process['first_response_time']=start_time
            
            run_process(process, start_event, end_event, start_time, process['burst_time']) #프로세스 실행
            last_end_time = start_time + process['burst_time'] #마지막 종료 시간 설정
    
    #Shortest Job First
    elif scheduling_type == "SJF":
        last_end_time = 0
        process_data.sort(key=lambda x: (x['arrive_time'], x['burst_time']))  #먼저 도착하고 실행시간이 짧은 순으로 정렬
        while arrival_index < len(process_data) or process_queue:
            #현재 시간 이전에 도착한 모든 프로세스를 큐에 추가
            while arrival_index < len(process_data) and process_data[arrival_index]['arrive_time'] <= current_time:
                process_queue.append(process_data[arrival_index])
                arrival_index += 1

            if process_queue:
                #큐에 존재하는 프로세스들 중 우선순위가 가장 높은 프로세스 선택
                process_queue.sort(key=lambda x: x['burst_time'])
                process = process_queue.pop(0)
                #다음에 들어올 프로세스의 도착시간과 이전 프로세스의 종료시간 사이에 idle한 시간이 존재한다면 빈 간트차트 출력  
                if process['arrive_time']>last_end_time:
                    run_idle_process(last_end_time,process['arrive_time']-last_end_time)

                start_time = max(current_time, process['arrive_time']) #시작 시간 설정
                if process['first_response_time'] is None: #response time 설정
                    process['first_response_time'] = start_time
                process['start_times'].append(start_time)
                process['execution_times'].append(process['burst_time'])
                process['end_times'].append(start_time + process['burst_time'])
                last_end_time = start_time+process['burst_time'] #마지막 프로세스 종료시간 설정

                run_process(process, start_event, end_event, start_time, process['burst_time']) #프로세스 실행

                #실행된 프로세스의 종료 시간 갱신
                current_time = start_time + process['burst_time']
            else:
                #큐가 비었다면 다음 프로세스의 도착 시간으로 시간 점프
                if arrival_index < len(process_data):
                    current_time = process_data[arrival_index]['arrive_time']

    #Shortest Remaining Time First
    elif scheduling_type == "SRTF":
        last_end_time = 0
        process_data.sort(key=lambda x:(x['arrive_time'], x['burst_time'])) #먼저 도착하고 실행시간이 짧은 순으로 정렬
        while arrival_index < len(process_data) or process_queue:
            #현재 시간 이전에 도착한 모든 프로세스를 큐에 추가
            while arrival_index < len(process_data) and process_data[arrival_index]['arrive_time'] <= current_time:
                new_process = process_data[arrival_index]
                new_process['remaining_time'] = new_process['burst_time']  # 초기 remaining time 설정
                new_process['start_time'] = max(current_time, new_process['arrive_time'])  # 시작 시간 설정
                process_queue.append(new_process)
                arrival_index += 1
                
            if process_queue:
                #큐에 존재하는 프로세스들 중 잔여 시간이 가장 짧은 프로세스 선택
                process_queue.sort(key=lambda x: x['remaining_time'])
                process = process_queue.pop(0)
                actual_start_time = max(current_time, process['start_time'] if 'start_time' in process else current_time)
                #다음에 들어올 프로세스의 도착시간과 이전 프로세스의 종료시간 사이에 idle한 시간이 존재한다면 빈 간트차트 출력
                if process['arrive_time']>last_end_time:
                    run_idle_process(last_end_time,process['arrive_time']-last_end_time)
                
                execution_time = process['remaining_time'] #실행시간을 잔여시간으로 설정
                if process['first_response_time'] is None: #response time 설정
                    process['first_response_time'] = actual_start_time

                #현재 프로세스가 실행되는 동안 도착하는 프로세스들 큐에 넣기
                while arrival_index < len(process_data) and process_data[arrival_index]['arrive_time'] <= actual_start_time+execution_time:
                    new_process = process_data[arrival_index]
                    new_process['remaining_time'] = new_process['burst_time']  # 초기 remaining_time 설정
                    new_process['start_time'] = max(current_time, new_process['arrive_time'])  #시작 시간 설정
                    process_queue.append(new_process)
                    arrival_index += 1
                    #새롭게 도착하는 프로세스의 실행시간이 현재 프로세스의 남은 실행시간보다 적다면 해당 프로세스가 도착할 때까지 실행
                    if new_process['burst_time']<process['remaining_time']-actual_start_time+new_process['arrive_time']:
                        execution_time = min(execution_time,new_process['arrive_time']-actual_start_time)  
                        break  

                process['start_times'].append(actual_start_time)
                process['execution_times'].append(execution_time)
                end_time = actual_start_time + execution_time
                process['end_times'].append(end_time)
                process['remaining_time'] -= execution_time
                last_end_time = end_time

                # 프로세스 실행
                run_process(process, start_event, end_event, actual_start_time, execution_time)

            
                # 남은 실행 시간이 있다면 큐의 끝으로
                if process['remaining_time'] > 0:
                    process['start_time'] = actual_start_time + execution_time  # 다음 실행 시작 시간 업데이트
                    process_queue.append(process) 
                # 현재 시간 업데이트
                current_time = actual_start_time + execution_time
                
            else:
                # 큐가 비었다면 다음 프로세스의 도착 시간으로 시간 점프
                if arrival_index < len(process_data):
                    current_time = process_data[arrival_index]['arrive_time']

    #Round-Robin
    elif scheduling_type == "Round-Robin":
        last_end_time = 0
        process_data.sort(key=lambda x: x['arrive_time']) #프로세스들 도착 시간 기준으로 정렬
        while arrival_index < len(process_data) or process_queue:
            #현재 시간 이전에 도착한 모든 프로세스를 큐에 추가
            while arrival_index < len(process_data) and process_data[arrival_index]['arrive_time'] <= current_time:
                new_process = process_data[arrival_index]
                new_process['remaining_time'] = new_process['burst_time']  # 초기 remaining time 설정
                new_process['start_time'] = max(current_time, new_process['arrive_time'])  # 시작 시간 설정
                process_queue.append(new_process)
                arrival_index += 1

            if process_queue:
                process = process_queue.pop(0)
                actual_start_time = max(current_time, process['start_time'] if 'start_time' in process else current_time)
                #다음에 들어올 프로세스의 도착시간과 이전 프로세스의 종료시간 사이에 idle한 시간이 존재한다면 빈 간트차트 출력
                if process['arrive_time']>last_end_time:
                    run_idle_process(last_end_time,process['arrive_time']-last_end_time)

                execution_time = min(process['remaining_time'], time_quantum)
                if process['first_response_time'] is None:
                    process['first_response_time'] = actual_start_time

                process['start_times'].append(actual_start_time)
                process['execution_times'].append(execution_time)
                end_time = actual_start_time + execution_time
                process['end_times'].append(end_time)
                process['remaining_time'] -= execution_time
                last_end_time = end_time

                # 프로세스 실행
                run_process(process, start_event, end_event, actual_start_time, execution_time)

                #현재 프로세스가 실행되는 동안 도착하는 프로세스들 큐에 넣기
                while arrival_index < len(process_data) and process_data[arrival_index]['arrive_time'] <= actual_start_time+execution_time:
                    new_process = process_data[arrival_index]
                    new_process['remaining_time'] = new_process['burst_time']  # 초기 remaining_time 설정
                    new_process['start_time'] = max(current_time, new_process['arrive_time'])  # 시작 시간 설정
                    process_queue.append(new_process)
                    arrival_index += 1

                # 남은 실행 시간이 있다면 큐의 끝으로
                if process['remaining_time'] > 0:
                    process['start_time'] = actual_start_time + execution_time  # 다음 실행 시작 시간 업데이트
                    process_queue.append(process)
                # 현재 시간 업데이트
                current_time = actual_start_time + execution_time
                
            else:
                # 큐가 비었다면 다음 프로세스의 도착 시간으로 시간 점프
                if arrival_index < len(process_data):
                    current_time = process_data[arrival_index]['arrive_time']

    #비선점형 우선순위
    elif scheduling_type=="Priority(Non Preemptive)":
        last_end_time = 0
        #먼저 도착하고 우선순위가 높은 순으로 정렬
        process_data.sort(key=lambda x:(x['arrive_time'], x['priority']))
        while arrival_index < len(process_data) or process_queue:
            # 현재 시간 이전에 도착한 모든 프로세스를 큐에 추가
            while arrival_index < len(process_data) and process_data[arrival_index]['arrive_time'] <= current_time:
                process_queue.append(process_data[arrival_index])
                arrival_index += 1

            if process_queue:
                # 우선순위가 가장 높은 프로세스 선택
                process_queue.sort(key=lambda x: -x['priority'])
                process = process_queue.pop(0)
                #다음에 들어올 프로세스의 도착시간과 이전 프로세스의 종료시간 사이에 idle한 시간이 존재한다면 빈 간트차트 출력
                if process['arrive_time']>last_end_time:
                    run_idle_process(last_end_time,process['arrive_time']-last_end_time)
                
                start_time = max(current_time, process['arrive_time']) 
                if process['first_response_time'] is None:
                    process['first_response_time'] = start_time
                process['start_times'].append(start_time)
                process['execution_times'].append(process['burst_time'])
                process['end_times'].append(start_time + process['burst_time'])
                run_process(process, start_event, end_event, start_time, process['burst_time'])
                last_end_time = start_time +process['burst_time']

                # 실행된 프로세스의 종료 시간 갱신
                current_time = start_time + process['burst_time']
            else:
                # 큐가 비어 있으면 다음 프로세스 도착 시간으로 점프
                if arrival_index < len(process_data):
                    current_time = process_data[arrival_index]['arrive_time']

    #선점형 우선순위
    elif scheduling_type == "Priority(Preemptive)":
        last_end_time=0
        #먼저 도착하고 우선순위가 높은 순으로 정렬
        process_data.sort(key=lambda x:(x['arrive_time'], x['priority']))
        while arrival_index < len(process_data) or process_queue:
            # 현재 시간 이전에 도착한 모든 프로세스를 큐에 추가
            while arrival_index < len(process_data) and process_data[arrival_index]['arrive_time'] <= current_time:
                new_process = process_data[arrival_index]
                new_process['remaining_time'] = new_process['burst_time']  # 초기 remaining time 설정
                new_process['start_time'] = max(current_time, new_process['arrive_time'])  # 시작 시간 설정
                process_queue.append(new_process)
                arrival_index += 1
                
            if process_queue:
                process_queue.sort(key=lambda x: -x['priority'])
                process = process_queue.pop(0)
                actual_start_time = max(current_time, process['start_time'] if 'start_time' in process else current_time)
                #다음에 들어올 프로세스의 도착시간과 이전 프로세스의 종료시간 사이에 idle한 시간이 존재한다면 빈 간트차트 출력
                if process['arrive_time']>last_end_time:
                    run_idle_process(last_end_time,process['arrive_time']-last_end_time)

                execution_time = process['remaining_time']
                if process['first_response_time'] is None:
                    process['first_response_time'] = actual_start_time

                #현재 프로세스가 실행되는 동안 도착하는 프로세스들 큐에 넣기
                while arrival_index < len(process_data) and process_data[arrival_index]['arrive_time'] <= actual_start_time+execution_time:
                    new_process = process_data[arrival_index]
                    new_process['remaining_time'] = new_process['burst_time']  # 초기 remaining time 설정
                    new_process['start_time'] = max(current_time, new_process['arrive_time'])  # 시작 시간 설정
                    process_queue.append(new_process)
                    arrival_index += 1
                    #새롭게 도착하는 프로세스의 우선순위가 현재 프로세스의 우선순위보다 높다면 해당 프로세스가 도착할 때까지 실행
                    if new_process['priority']<process['priority']:
                        execution_time = min(execution_time,new_process['arrive_time']-actual_start_time)  
                        break  

                process['start_times'].append(actual_start_time)
                process['execution_times'].append(execution_time)
                end_time = actual_start_time + execution_time
                process['end_times'].append(end_time)
                process['remaining_time'] -= execution_time
                last_end_time = end_time

                # 프로세스 실행
                run_process(process, start_event, end_event, actual_start_time, execution_time)

            
                # 남은 실행 시간이 있다면 큐의 끝으로
                if process['remaining_time'] > 0:
                    process['start_time'] = actual_start_time + execution_time  # 다음 실행 시작 시간 업데이트
                    process_queue.append(process)
                # 현재 시간 업데이트
                current_time = actual_start_time + execution_time
                
            else:
                # 큐가 비었다면 다음 프로세스의 도착 시간으로 시간 점프
                if arrival_index < len(process_data):
                    current_time = process_data[arrival_index]['arrive_time']


    #신규 : 우선순위 기반 라운드로빈
    elif scheduling_type == "Priority based Round-Robin":
        last_end_time = 0
        process_data.sort(key=lambda x: x['arrive_time']) #프로세스들 도착 시간 기준으로 정렬
        while arrival_index < len(process_data) or process_queue:
            #현재 시간 이전에 도착한 모든 프로세스를 큐에 추가
            while arrival_index < len(process_data) and process_data[arrival_index]['arrive_time'] <= current_time:
                new_process = process_data[arrival_index]
                new_process['remaining_time'] = new_process['burst_time']  # 초기 remaining time 설정
                new_process['start_time'] = max(current_time, new_process['arrive_time'])  # 시작 시간 설정
                process_queue.append(new_process)
                arrival_index += 1

            if process_queue:
                process = process_queue.pop(0)
                actual_start_time = max(current_time, process['start_time'] if 'start_time' in process else current_time)
                #다음에 들어올 프로세스의 도착시간과 이전 프로세스의 종료시간 사이에 idle한 시간이 존재한다면 빈 간트차트 출력
                if process['arrive_time']>last_end_time:
                    run_idle_process(last_end_time,process['arrive_time']-last_end_time)

                execution_time = min(process['remaining_time'], process['time_quantum'])
                if process['first_response_time'] is None:
                    process['first_response_time'] = actual_start_time

                process['start_times'].append(actual_start_time)
                process['execution_times'].append(execution_time)
                end_time = actual_start_time + execution_time
                process['end_times'].append(end_time)
                process['remaining_time'] -= execution_time
                last_end_time = end_time

                # 프로세스 실행
                run_process(process, start_event, end_event, actual_start_time, execution_time)

                #현재 프로세스가 실행되는 동안 도착하는 프로세스들 큐에 넣기
                while arrival_index < len(process_data) and process_data[arrival_index]['arrive_time'] <= actual_start_time+execution_time:
                    new_process = process_data[arrival_index]
                    new_process['remaining_time'] = new_process['burst_time']  # 초기 remaining_time 설정
                    new_process['start_time'] = max(current_time, new_process['arrive_time'])  # 시작 시간 설정
                    process_queue.append(new_process)
                    arrival_index += 1

                # 남은 실행 시간이 있다면 큐의 끝으로
                if process['remaining_time'] > 0:
                    process['start_time'] = actual_start_time + execution_time  # 다음 실행 시작 시간 업데이트
                    process_queue.append(process)
                # 현재 시간 업데이트
                current_time = actual_start_time + execution_time
                
            else:
                # 큐가 비었다면 다음 프로세스의 도착 시간으로 시간 점프
                if arrival_index < len(process_data):
                    current_time = process_data[arrival_index]['arrive_time']
    
    #신규 : 에이징을 추가한 라운드로빈
    elif scheduling_type == "Round-Robin with aging":
        last_end_time = 0
        process_data.sort(key=lambda x: x['arrive_time']) #프로세스들 도착 시간 기준으로 정렬
        for temp_process in process_data:
            temp_process['priority'] = 1
        while arrival_index < len(process_data) or process_queue:
            
            #현재 시간 이전에 도착한 모든 프로세스를 큐에 추가
            while arrival_index < len(process_data) and process_data[arrival_index]['arrive_time'] <= current_time:
                new_process = process_data[arrival_index]
                new_process['remaining_time'] = new_process['burst_time']  # 초기 remaining time 설정
                new_process['start_time'] = max(current_time, new_process['arrive_time'])  # 시작 시간 설정
                new_process['waiting_time'] = current_time-new_process['arrive_time']
                new_process['priority'] = (new_process['waiting_time']+new_process['burst_time'])/new_process['burst_time']
                process_queue.append(new_process)
                arrival_index += 1

            #큐에 존재하는 프로세스들의 우선순위 기준으로 재정렬
            process_queue.sort(key=lambda x: -x['priority'])

            if process_queue:
                process = process_queue.pop(0)
                actual_start_time = max(current_time, process['start_time'] if 'start_time' in process else current_time)
                #다음에 들어올 프로세스의 도착시간과 이전 프로세스의 종료시간 사이에 idle한 시간이 존재한다면 빈 간트차트 출력
                if process['arrive_time']>last_end_time:
                    run_idle_process(last_end_time,process['arrive_time']-last_end_time)

                execution_time = min(process['remaining_time'], time_quantum)
                if process['first_response_time'] is None:
                    process['first_response_time'] = actual_start_time

                process['start_times'].append(actual_start_time)
                process['execution_times'].append(execution_time)
                end_time = actual_start_time + execution_time
                process['end_times'].append(end_time)
                process['remaining_time'] -= execution_time
                last_end_time = end_time

                #aging 계산
                for temp_process in process_queue:
                    if temp_process['end_times']:
                        end_time = temp_process['end_times'][-1]
                        temp_process['waiting_time'] += current_time+execution_time-end_time
        
                    temp_process['priority'] = (temp_process['waiting_time']+temp_process['remaining_time'])/temp_process['remaining_time']
                    
                    for refresh_process in process_data:
                        if refresh_process['name'] == temp_process['name']:
                            refresh_process['priority'] = temp_process['priority']
                            break

                # 프로세스 실행
                run_process(process, start_event, end_event, actual_start_time, execution_time)

                #현재 프로세스가 실행되는 동안 도착하는 프로세스들 큐에 넣기
                while arrival_index < len(process_data) and process_data[arrival_index]['arrive_time'] <= actual_start_time+execution_time:
                    new_process = process_data[arrival_index]
                    new_process['remaining_time'] = new_process['burst_time']  # 초기 remaining_time 설정
                    new_process['start_time'] = max(current_time, new_process['arrive_time'])  # 시작 시간 설정
                    new_process['waiting_time'] = current_time+execution_time-new_process['arrive_time']
                    new_process['priority'] = (new_process['waiting_time']+new_process['burst_time'])/new_process['burst_time']
                    process_queue.append(new_process)
                    arrival_index += 1

                # 남은 실행 시간이 있다면 큐의 끝으로
                if process['remaining_time'] > 0:
                    process['start_time'] = actual_start_time + execution_time  # 다음 실행 시작 시간 업데이트
                    process_queue.append(process)
                # 현재 시간 업데이트
                current_time = actual_start_time + execution_time
                
            else:
                # 큐가 비었다면 다음 프로세스의 도착 시간으로 시간 점프
                if arrival_index < len(process_data):
                    current_time = process_data[arrival_index]['arrive_time']

    #신규 : 데드라인 기반 에이징
    elif scheduling_type == "Deadline based aging":
        last_end_time = 0
        process_data.sort(key=lambda x: (x['arrive_time'],x['deadline'])) #프로세스들 도착 시간 기준으로 정렬
        for temp_process in process_data:
            temp_process['priority'] = 0
        while arrival_index < len(process_data) or process_queue:
        
            #현재 시간 이전에 도착한 모든 프로세스를 큐에 추가
            while arrival_index < len(process_data) and process_data[arrival_index]['arrive_time'] <= current_time:
                new_process = process_data[arrival_index]
                new_process['start_time'] = max(current_time, new_process['arrive_time'])  # 시작 시간 설정
                new_process['deadline'] = new_process['deadline'] - current_time
                process_queue.append(new_process)
                arrival_index += 1

            #큐에 존재하는 프로세스들의 우선순위 기준으로 재정렬
            for process in process_queue:
                process['priority'] = (current_time - process['arrive_time']) / process['deadline']

            process_queue.sort(key=lambda x: -x['priority'])

            if process_queue:
                process = process_queue.pop(0)
                actual_start_time = max(current_time, process['start_time'] if 'start_time' in process else current_time)
                #다음에 들어올 프로세스의 도착시간과 이전 프로세스의 종료시간 사이에 idle한 시간이 존재한다면 빈 간트차트 출력
                if process['arrive_time'] > last_end_time:
                    run_idle_process(last_end_time, process['arrive_time'] - last_end_time)

                execution_time = process['burst_time']
                if process['first_response_time'] is None:
                    process['first_response_time'] = actual_start_time

                process['start_times'].append(actual_start_time)
                process['execution_times'].append(execution_time)
                end_time = actual_start_time + execution_time
                process['end_times'].append(end_time)
                last_end_time = end_time

                #aging 계산
                for temp_process in process_queue:
                    temp_process['deadline'] -= execution_time
                    temp_process['priority'] = (current_time - temp_process['arrive_time']) / temp_process['deadline']
                    for refresh_process in process_data:
                        if refresh_process['name'] == temp_process['name']:
                            refresh_process['priority'] = temp_process['priority']
                            break

                # 프로세스 실행
                run_process(process, start_event, end_event, actual_start_time, execution_time)

                #현재 프로세스가 실행되는 동안 도착하는 프로세스들 큐에 넣기
                while arrival_index < len(process_data) and process_data[arrival_index]['arrive_time'] <= actual_start_time + execution_time:
                    new_process = process_data[arrival_index]
                    new_process['start_time'] = max(current_time, new_process['arrive_time'])  # 시작 시간 설정
                    new_process['deadline'] -= actual_start_time
                    new_process['priority'] = (current_time - new_process['arrive_time']) / new_process['deadline']
                    process_queue.append(new_process)
                    arrival_index += 1

               # 현재 시간 업데이트
                current_time = actual_start_time + execution_time
            
            else:
                # 큐가 비었다면 다음 프로세스의 도착 시간으로 시간 점프
                if arrival_index < len(process_data):
                    current_time = process_data[arrival_index]['arrive_time']


        #프로세스 실행 결과 계산
        calculate_metrics(process_data)
        process_data = []  # 프로세스 데이터 초기화

#리셋 함수
def reset_simulation():
    process_data.clear()
    gantt_chart.clear()
    timer_var.set("Time elapsed: 0s")
    process_listbox.delete(0,tk.END)

def validate_priority(*args):
    if(priority_var.get().strip()==""):
        return
    try:
        # 입력된 값이 숫자인지 확인
        value = int(priority_var.get())
        if not (0 <= value <= 49):
            # 값이 범위를 벗어나면 경고하고 원래 값으로 재설정
            raise ValueError("우선순위는 0~49의 정수로 작성해야합니다.")
    except ValueError as e:
        # 입력값이 유효하지 않은 경우 에러 메시지 표시
        messagebox.showerror("잘못된 입력", str(e))
        priority_var.set('')  # 필드 클리어

#사용 방법 설명
def show_instructions():
    instructions = (
        "Processor Scheduling Simulation 사용 방법:\n\n"
        "1. Scheduling Type: 스케줄링 유형을 선택하세요.\n"
        "2. Processor Name: 프로세스 이름을 입력하세요.\n"
        "3. Burst Time: 프로세스의 실행 시간을 입력하세요.\n"
        "4. Arrive Time: 프로세스의 도착 시간을 입력하세요.\n"
        "5. Priority: 프로세스의 우선순위를 입력하세요 (0 ~ 49의 정수).\n"
        "6. 각 알고리즘에 따라 필요한 추가 정보(deadline)입력창이 생기면 해당 정보를 입력하세요.\n"
        "7. Add Process: 입력한 정보를 바탕으로 프로세스를 추가하세요.\n"
        "8. Time quantum: 선택한 스케줄링이 Round-Robin 혹은 Round-Robin with aging이라면 time quantum값을 입력하세요.\n"
        "9. Start Simulation: 시뮬레이션을 시작합니다.\n"
        "10. Simulation Result: 시뮬레이션을 결과를 확인합니다.\n"
        "11. Reset Simulation: 시뮬레이션을 초기화합니다.\n"
        "12. 스케줄링 알고리즘 설명을 보려면 ? 버튼을 클릭하세요."
    )
    messagebox.showinfo("사용 방법", instructions)

#각 알고리즘에 대한 설명
def show_scheduling_description():
    scheduling_description = {
        "FCFS": "First-Come, First-Served (FCFS)는 가장 간단한 스케줄링 알고리즘으로, 먼저 도착한 프로세스를 먼저 처리합니다.",
        "SJF": "Shortest Job First (SJF)는 실행 시간이 가장 짧은 프로세스를 먼저 실행합니다.",
        "SRTF": "Shortest Remaining Time First (SRTF)는 SJF의 선점형으로 남은 실행 시간이 가장 짧은 프로세스를 우선적으로 실행합니다.",
        "Round-Robin": "라운드 로빈은 각 프로세스에 동일한 시간(타임 퀀텀)만큼 CPU를 할당한 후, 완료되지 않은 프로세스를 대기열 끝으로 이동시킵니다. 해당 알고리즘을 사용하기 위해서는 time quantum을 입력해야 합니다.",
        "Priority(Non Preemptive)": "우선순위(비선점)는 각 프로세스에 우선순위를 할당하고, 가장 높은 우선순위를 가진 프로세스부터 실행합니다. (Priority(Non Preemptive)의 우선순위는 49에 가까울수록 우선순위가 높습니다.)",
        "Priority(Preemptive)": "우선순위(선점)는 더 높은 우선순위의 프로세스가 도착하면 현재 실행 중인 프로세스를 중단시키고 새 프로세스를 실행합니다. (Priority(Preemptive)의 우선순위는 49에 가까울수록 우선순위가 높습니다.)",
        "Priority based Round-Robin": "우선순위 기반 라운드 로빈은 입력받은 0~49의 우선순위에 따라 타임 퀀텀을 조절하여 라운드 로빈 스케줄링을 수행합니다.\n0~9:1\n10~19:2\n20~29:3\n30~39:4\n40~49:5\n(Priority based Round-Robin의 우선순위는 49에 가까울수록 우선순위가 높습니다.)",
        "Round-Robin with aging": "라운드 로빈 에이징은 라운드 로빈을 기반으로 실행 대기 시간에 따라 우선순위를 조정합니다. 해당 알고리즘을 사용하기 위해서는 time quantum을 입력해야 합니다.(Round-Robin with aging의 우선순위는 49에 가까울수록 우선순위가 높습니다.)",
        "Deadline based aging": "데드라인 기반 에이징은 각 프로세스의 데드라인을 고려하여 우선순위를 조정하고 스케줄링합니다. 해당 알고리즘을 사용하기 위해서는 각 프로세스의 Deadline을 입력해야 합니다. (우선순위 = 대기시간/데드라인까지 남은 시간) (Deadline based aging의 우선순위는 49에 가까울수록 우선순위가 높습니다.)"
    }
    selected_type = scheduling_type.get()
    description = scheduling_description.get(selected_type, "선택한 스케줄링 알고리즘에 대한 설명이 없습니다.")
    messagebox.showinfo("스케줄링 알고리즘 설명", description)

processor_name_var = tk.StringVar()
burst_time_var = tk.StringVar()
arrive_time_var = tk.StringVar()
priority_var = tk.StringVar()
priority_var.trace("w", validate_priority)  
scheduling_type = tk.StringVar(value="FIFO")

time_quantum_var = tk.StringVar()
time_quantum_label = ttk.Label(root, text="Time Quantum:")
time_quantum_entry = ttk.Entry(root, textvariable=time_quantum_var)

deadline_var = tk.StringVar()
deadline_label = ttk.Label(root, text="DeadLine:")
deadline_entry = ttk.Entry(root, textvariable=deadline_var)

scheduling_type_changed()  

ttk.Label(root, textvariable=timer_var).pack(pady=10)  #타이머 표시

process_listbox = tk.Listbox(root, height=10, width=70)  #프로세스 목록 및 결과 출력 화면
process_listbox.pack(pady=10)

help_button = ttk.Button(root, text="Show Instructions", command=show_instructions) #사용 방법 메시지박스 버튼
help_button.pack(pady=10)

scheduling_frame = ttk.Frame(root)
scheduling_frame.pack(fill='x', padx=10, pady=2)

#스케줄링 알고리즘 선택 드롭박스
ttk.Label(scheduling_frame, text="Scheduling Type:").grid(row=0, column=0, sticky='w')
scheduling_menu = ttk.Combobox(scheduling_frame, textvariable=scheduling_type, state='readonly', values=["FCFS", "SJF","SRTF","Round-Robin","Priority(Non Preemptive)","Priority(Preemptive)","Priority based Round-Robin","Round-Robin with aging","Deadline based aging"])
scheduling_menu.grid(row=0, column=1, sticky='ew')
scheduling_menu.bind('<<ComboboxSelected>>', scheduling_type_changed)
scheduling_menu.current(0)

info_button = ttk.Button(scheduling_frame, text="?", command=show_scheduling_description)
info_button.grid(row=0,column=2,padx=5)

scheduling_frame.columnconfigure(1, weight=1)  

#시뮬레이션 시작 버튼
start_button = ttk.Button(root, text="Start Simulation", command=start_simulation)
start_button.pack(pady=10)

#리셋 버튼
reset_button = ttk.Button(root, text="Reset Simulation", command=reset_simulation)
reset_button.pack(pady=10)

#프로세스 추가 버튼
add_button = ttk.Button(root, text="Add Process", command=add_process)
add_button.pack(pady=10)

#프로세스 이름 입력
ttk.Label(root, text="Processor Name:").pack(fill='x', padx=10)  
processor_name_entry = ttk.Entry(root, textvariable=processor_name_var)
processor_name_entry.pack(fill='x', padx=10, pady=2)

#프로세스 실행시간 입력
ttk.Label(root, text="Burst Time:").pack(fill='x', padx=10)
burst_time_entry = ttk.Entry(root, textvariable=burst_time_var)
burst_time_entry.pack(fill='x', padx=10, pady=2)

#프로세스 도착시간 입력
ttk.Label(root, text="Arrive Time:").pack(fill='x', padx=10)
arrive_time_entry = ttk.Entry(root, textvariable=arrive_time_var)
arrive_time_entry.pack(fill='x', padx =10, pady= 2)

#프로세스 우선순위 입력
ttk.Label(root, text="Priority(0 ~ 49의 정수 입력):").pack(fill='x', padx= 10)
priority_entry = ttk.Entry(root, textvariable=priority_var)
priority_entry.pack(fill='x', padx= 10, pady= 2)

root.mainloop()
