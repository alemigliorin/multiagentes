'use client'

import ChatInput from './ChatInput'
import MessageArea from './MessageArea'

const ChatArea = () => {
  return (
    <main className="relative flex flex-grow flex-col bg-background">
      <MessageArea />
      <div className="sticky bottom-0 px-4 pb-4">
        <ChatInput />
      </div>
    </main>
  )
}

export default ChatArea
