import SublimeREPL.text_transfer as text_transfer
import re, sublime
from SublimeREPL.sublimerepl import manager

DIVIDER = "-------------"

class ClojureReplExtensionsCommand(text_transfer.ReplTransferCurrent):
    def run(self, edit, command):
        text = ""

        if command == "run-all-tests":
            text = self.run_all_tests()
        elif command == "run-tests":
            text = self.run_tests()
        elif command == "exit":
            text = self.run_exit()
        elif command == "switch-namespace":
            text = self.run_require()
        elif command == "reload":
            text = self.run_reload()
        elif command == "reload-all":
            text = self.run_reload_all()
        elif command == "doc":
            text = self.run_doc()
        elif command == "source":
            text = self.run_source()
        elif command == "dir":
            text = self.run_dir()

        self.send_to_repl(text)
        if command == "switch-namespace":
            self.copy_to_repl(self.run_in_ns())

    def send_to_repl(self, text):
        cmd = 'repl_send'
        self.view.window().run_command(cmd, {"external_id": self.repl_external_id(), "text": text})

    def copy_to_repl(self, text):
        external_id = self.repl_external_id()
        for rv in manager.find_repl(external_id):
          text += rv.repl.cmd_postfix
          rv.append_input_text(text)
          rv.adjust_end()
          rv.repl.write(text)
          break
        else:
          sublime.error_message("Cannot find REPL for '{}'".format(external_id))

    def run_all_tests(self):
        ns = self.current_namespace()
        root_namespace = ns.split(".")[0]
        return """
        (require 'clojure.test)
        (let [ns-pattern (re-pattern (str "^" "{root_namespace}" ".+test$"))]
          (clojure.test/run-all-tests ns-pattern))
        """.format(root_namespace=root_namespace)

    def run_tests(self):
        ns = self.current_namespace()
        if ns.find("-test"):
            ns = ns.replace("-test", "")
        test_ns = ns + "-test"
        return """
        (require 'clojure.test)
        (require '{ns} :reload)
        (require '{test_ns} :reload)
        (clojure.test/run-tests '{test_ns})
        """.format(ns=ns, test_ns=test_ns)

    def run_exit(self):
        return "(System/exit 0)"

    def run_require(self):
        ns = self.current_namespace(search_in_repl=False)
        if not ns:
            return
        return "(require '{ns})".format(ns=ns)

    def run_in_ns(self):
        ns = self.current_namespace(search_in_repl=False)
        if not ns:
            return
        return "(in-ns '{ns})".format(ns=ns)

    def run_reload(self):
        ns = self.current_namespace()
        return """
        (require '{ns} :reload)
        (println)
        (println "{divider}")
        (println (str "{ns}" " reloaded!"))
        """.format(ns=ns, divider=DIVIDER)

    def run_reload_all(self):
        ns = self.current_namespace()
        return """
        (require '{ns} :reload-all)
        (println)
        (println "{divider}")
        (println (str "{ns}" " reloaded!"))
        """.format(ns=ns, divider=DIVIDER)

    def run_doc(self):
        identifier = self.selected_identifier()
        return """
        (clojure.repl/doc {identifier})
        """.format(identifier=identifier)

    def run_source(self):
        identifier = self.selected_identifier()
        return """
        (clojure.repl/source {identifier})
        """.format(identifier=identifier)

    def run_dir(self):
        ns = self.selected_text()
        return """
        (println)
        (println "{divider}")
        (clojure.repl/dir {ns})
        """.format(ns=ns, divider=DIVIDER)

    def current_namespace(self, search_in_repl=True):
        file_text = self.selected_file()
        file_lines = file_text.split("\n")

        # Search in a file window
        for line in file_lines:
            match = re.match("^\s*\(ns ([a-zA-Z0-9.-]+)[)\s]*", line)
            if match:
                return match.group(1)

        # Search in a REPL window
        if search_in_repl:
            for line in reversed(file_lines):
                match = re.match("^([a-zA-Z0-9.-]+)=>", line)
                if match:
                    return match.group(1)

        sublime.error_message('You must run it in a window with clojure code.')
        return ""

    def selected_identifier(self):
        v = self.view
        strs = []
        old_sel = list(v.sel())
        v.run_command("expand_selection", {"to": "word"})
        for s in v.sel():
            strs.append(v.substr(s))
        v.sel().clear()
        for s in old_sel:
            v.sel().add(s)
        return "\n\n".join(strs)
