import { CommonModule } from '@angular/common';
import { Component, ElementRef, Input, OnInit, ViewChild, AfterViewChecked, ChangeDetectorRef, SimpleChanges, EventEmitter, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../services/chat.service';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { HighchartsChartModule } from 'highcharts-angular';
import * as Highcharts from 'highcharts';
import ExportingModule from 'highcharts/modules/exporting';
import ExportDataModule from 'highcharts/modules/export-data';

@Component({
    selector: 'app-chat',
    standalone: true,
    imports: [
      CommonModule, 
      FormsModule,
      HttpClientModule,
      HighchartsChartModule
    ],
    templateUrl: './chat.component.html',
    styleUrl: './chat.component.scss'
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @Input() isCollapsed = false;
  @Input() currentChatId: string | null = null;
  @Output() requestChatsReload = new EventEmitter<void>();
  @Output() chatNotEmpty = new EventEmitter<void>();
  @Output() chatEmpty = new EventEmitter<void>();
  
  @ViewChild('chatInput') chatInput!: ElementRef;
  @ViewChild('messagesEnd') messagesEnd!: ElementRef;
  
  inputText = '';
  messages: any[] = [];
  isTyping = false;
  isListening = false;
  recognition: any;
  initials: string = '';
  Highcharts = Highcharts;
  
  // Track if we need to scroll to bottom
  private shouldScrollToBottom = false;
  private previousMessageCount = 0;

  constructor(
    private chatService: ChatService,
    private cdRef: ChangeDetectorRef
  ) {
        // Dynamically load Highcharts export-related modules (works across ESM/CJS builds)
        if (typeof window !== 'undefined') {
          Promise.all([
            import('highcharts/modules/exporting'),
            import('highcharts/modules/export-data'),
            import('highcharts/modules/full-screen')
          ]).then(([exporting, exportData, fullScreen]) => {
            const exp: any = exporting;
            if (typeof exp === 'function') {
              exp(Highcharts);
            } else if (exp && typeof exp.default === 'function') {
              exp.default(Highcharts);
            }
            const expData: any = exportData;
            if (typeof expData === 'function') {
              expData(Highcharts);
            } else if (expData && typeof expData.default === 'function') {
              expData.default(Highcharts);
            }
            const fs: any = fullScreen;
            if (typeof fs === 'function') {
              fs(Highcharts);
            } else if (fs && typeof fs.default === 'function') {
              fs.default(Highcharts);
            }
            // Ensure exporting is globally enabled and custom menu includes CSV, XLS, print, fullscreen
            Highcharts.setOptions({
              exporting: {
                enabled: true,
                buttons: {
                  contextButton: {
                    menuItems: [
                      'downloadPNG',
                      'downloadJPEG',
                      'downloadPDF',
                      'downloadSVG',
                      'separator',
                      'downloadCSV',
                      'downloadXLS',
                      'separator',
                      'printChart',
                      'viewFullscreen'
                    ]
                  }
                }
              }
            });
          });
        }
  }

  ngOnInit() {
    this.initSpeechRecognition();
  }

  boldifyMarkdown(text: string): string {
    return text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
  }
  
  ngOnChanges(changes: SimpleChanges) {
    if (changes['currentChatId']) {
      const id = changes['currentChatId'].currentValue;
      this.isTyping = false;
      if (!id || id === 'new' || id === null) {
        this.messages = [];
        this.inputText = '';
        this.shouldScrollToBottom = false;
        this.chatEmpty.emit(); // New chat is empty
        this.chatInput?.nativeElement?.focus();
      } else {
        this.loadPreviousMessages();
      }
    }
    
    // Handle portal changes - don't create new chat, just update portal
    if (changes['currentPortal'] && !changes['currentPortal'].firstChange) {
      // Portal changed, but keep current chat
      this.shouldScrollToBottom = false;
    }
  }

  ngAfterViewChecked() {
    // Only scroll if we have new messages
    if (this.shouldScrollToBottom && this.messages.length > this.previousMessageCount) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
      this.previousMessageCount = this.messages.length;
    }
  }

  get filteredMessages() {
    return this.messages.filter(m => m.chatId === this.currentChatId);
  }

  // Check if current chat is empty
  get isCurrentChatEmpty(): boolean {
    return this.messages.length === 0 || this.messages.every(m => !m.text || m.text.trim() === '');
  }


  logout() {
    localStorage.removeItem('authToken');
    window.location.href = 'https://fealtytechnologies.com/';
  }

  adjustTextareaHeight() {
    const textarea = this.chatInput.nativeElement;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 130) + 'px';
  }

  handleSend(event: Event) {
    if (!(event as KeyboardEvent).shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  scrollToBottom() {
    try {
      this.messagesEnd.nativeElement.scrollIntoView({ behavior: 'smooth' });
    } catch(err) { }
  }

  async startSampleChat(question: string) {
    this.inputText = question;
    await this.sendMessage();
  }

  async sendMessage() {
    const sendButton = document.getElementById('sendButton');
    const text = this.inputText.trim();
    if (!text || this.isTyping || !sendButton) return;
 
    this.isTyping = true;
    sendButton.style.pointerEvents = 'none';
   
    if (!this.currentChatId || this.currentChatId === 'new') {
      const resp: any = await this.chatService.newChatId().toPromise();
      this.currentChatId = resp.data.session_id;
      console.log('New Chat ID:', this.currentChatId);
    }

    // Add user message
    this.messages.push({
      id: Date.now(),
      text,
      isUser: true,
      chatId: this.currentChatId
    });

    // Notify parent that chat is no longer empty
    this.chatNotEmpty.emit();

    this.inputText = '';
    this.isTyping = true;
    this.shouldScrollToBottom = true;

    try {
      const response = await this.chatService.sendMessage(text, this.currentChatId).toPromise();
      const aiResponse = response.data.response;

      // Add AI message
      const aiMessage = {
        id: Date.now() + 1,
        text: aiResponse.text || "I couldn't process your request",
        charts: aiResponse.charts || [],
        isUser: false,
        chatId: this.currentChatId,
        html: aiResponse.html || '',   // ← capture HTML here too
      };
      
      if (this.messages.length <= 2) {
        this.requestChatsReload.emit();
      }
      this.messages.push(aiMessage);
      this.isTyping = false;
      this.shouldScrollToBottom = true;
    } catch (error) {
      console.error('Error:', error);
      this.handleApiError();
    } finally {
      sendButton.style.pointerEvents = 'auto';
    }
  }

  private handleApiError() {
    this.isTyping = false;
    const errorMessage = "Sorry, I'm having trouble connecting. Please try again later.";
    this.messages.push({
      id: Date.now() + 1,
      text: errorMessage,
      charts: [],
      isUser: false,
      chatId: this.currentChatId
    });
    this.shouldScrollToBottom = true;
  }

  initSpeechRecognition() {
    const SpeechRecognition = (window as any).SpeechRecognition ||
                             (window as any).webkitSpeechRecognition;
   
    if (!SpeechRecognition) {
      console.warn('Speech Recognition not supported');
      return;
    }
 
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';
 
    this.recognition.onresult = (event: any) => {
      const results = event.results[event.results.length - 1];
      this.inputText = results[0].transcript;
    };
 
    this.recognition.onend = () => {
      // Speech recognition ended
    };
  }
 
  toggleSpeechRecognition() {
    if (!this.isListening) {
      this.isListening = true;
      this.recognition.start();
    } else {
      this.isListening = false;
      this.recognition.stop();
    }
  }
  
  loadPreviousMessages() {
    this.chatService.previousMessage( this.currentChatId)
      .subscribe((response: any) => {
        if (!response.status || !response.data) {
          // No messages found, chat is empty
          this.chatEmpty.emit();
          return;
        }
 
        const session = response.data;
 
        // Convert session content to messages format
        this.messages = session.content.reduce((acc: any[], pair: any, i: any) => {
          acc.push({
            id: `${session.id}-${i}-u`,
            text: pair.human,
            isUser: true,
            chatId: session.id
          });
          acc.push({
            id: `${session.id}-${i}-b`,
            text: pair.ai.text,
            charts: pair.ai.charts || [],
            isUser: false,
            chatId: session.id,
            html: pair.ai.html || '',
          });
          return acc;
        }, []);

        // If we loaded messages, notify parent that chat is not empty
        if (this.messages.length > 0) {
          this.chatNotEmpty.emit();
        } else {
          // No messages in session, chat is empty
          this.chatEmpty.emit();
        }

        this.shouldScrollToBottom = true;
      }, (err: any) => {
        console.error(err);
        // On error, assume chat is empty
        this.chatEmpty.emit();
      });
  }
}