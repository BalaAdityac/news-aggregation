-- RLS policies for realtime.messages / messages table
CREATE TABLE IF NOT EXISTS public.messages (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid REFERENCES auth.users(id) NOT NULL,
    content text NOT NULL,
    channel_id text NOT NULL,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

-- Drop existings policies to ensure idempotency when running multiple times
DROP POLICY IF EXISTS "Users can insert their own messages" ON public.messages;
DROP POLICY IF EXISTS "Users can select messages in their private channel" ON public.messages;

-- Select policy: users can only see messages in their private channel (channel_id mapping to user_id)
CREATE POLICY "Users can insert their own messages" ON public.messages
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can select messages in their private channel" ON public.messages
    FOR SELECT USING (channel_id = auth.uid()::text);

-- Enable realtime for messages SAFELY
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_publication_tables
        WHERE pubname = 'supabase_realtime'
        AND schemaname = 'public'
        AND tablename = 'messages'
    ) THEN
        EXECUTE 'ALTER PUBLICATION supabase_realtime ADD TABLE public.messages';
    END IF;
EXCEPTION WHEN undefined_object THEN
    EXECUTE 'CREATE PUBLICATION supabase_realtime FOR TABLE public.messages';
END $$;

-- Storage objects RLS
-- Assuming a bucket named 'private_files'
insert into storage.buckets (id, name, public) values ('private_files', 'private_files', false) ON CONFLICT DO NOTHING;

DROP POLICY IF EXISTS "Users can upload their own files" ON storage.objects;
CREATE POLICY "Users can upload their own files" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'private_files' AND auth.uid()::text = (storage.foldername(name))[1]);

DROP POLICY IF EXISTS "Users can view their own files" ON storage.objects;
CREATE POLICY "Users can view their own files" ON storage.objects
    FOR SELECT USING (bucket_id = 'private_files' AND auth.uid()::text = (storage.foldername(name))[1]);

DROP POLICY IF EXISTS "Users can update their own files" ON storage.objects;
CREATE POLICY "Users can update their own files" ON storage.objects
    FOR UPDATE USING (bucket_id = 'private_files' AND auth.uid()::text = (storage.foldername(name))[1]);

DROP POLICY IF EXISTS "Users can delete their own files" ON storage.objects;
CREATE POLICY "Users can delete their own files" ON storage.objects
    FOR DELETE USING (bucket_id = 'private_files' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Add RLS on other hypothetical user-accessed tables, like saved_articles
CREATE TABLE IF NOT EXISTS public.saved_articles (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid REFERENCES auth.users(id) NOT NULL,
    article_id text NOT NULL,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(user_id, article_id)
);

ALTER TABLE public.saved_articles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can manage their own saved articles" ON public.saved_articles;
CREATE POLICY "Users can manage their own saved articles" ON public.saved_articles
    FOR ALL USING (auth.uid() = user_id);
